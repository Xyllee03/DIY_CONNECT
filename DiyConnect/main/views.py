from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import check_password
from .models import UserSites, UserPost, UserPost_BLOB, Friendships, UserMessages, MessageStatus,TaskRequest,Review,PostLike,FriendStatus, Notification, NotifyType,NotifyStatus, FogotPasswordFixed,Feedback
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
import time
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models.functions import Random
from django.db.models import Q, Max, OuterRef, Subquery, F,Case, When,Exists
from django.db import models
import random
import string

# Create your views here.


#initialized_cookie
@ensure_csrf_cookie
def set_csrf_token(request):
    return JsonResponse({"message": "CSRF token set"})


def index(request):
    context ={}
    return render(request, 'main/index.html', context)



# Authentication
def authentication_base(request):

    context ={}
    return render(request,'main/authentication/auth_base.html',context)

def authentication_login(request):
    if(request.method =="POST"):
        data = json.loads(request.body)    
        try:
            u_check = UserSites.objects.filter(username=data['username']).first()
           
            """
            print("Input Password:", data['password'])
            print("Stored Hashed Password:", u_check.password)
            print(data)
            print(u_check.password)
            print(check_password(data['password'], u_check.password))
            """
            if(check_password(data['password'], u_check.password)):
                user = authenticate(request, username=data['username'], password=data['password'])
                login(request, user)  # Log the user in
                request.session["RolesPostFilter"] = 'Innovator'
                return JsonResponse({"msg": "User has been retrieve", "redirect_url": "/diyconnect/home/"}, status=200)
            else:
                return JsonResponse({"error": "Invalid username or password."}, status=400)
        except:   
             return JsonResponse({"error": "Invalid username or password"}, status=400)
    context ={}
    return render(request,'main/authentication/auth_login.html',context)


def authentication_registration(request):
    context ={}
    return render(request,'main/authentication/auth_registration.html', context)

def authentication_forgot_password(request):
    context={
        
    }
    return render(request,'main/authentication/auth_forgot_pass.html', context)

def authentication_preLoad(request):
    if request.method =="POST":
        data = json.loads(request.body)        
        u_check = UserSites.objects.filter(username = data['username']).exists()
        if(u_check):
            return JsonResponse({"error": "The username has been used."}, status=400)        
        request.session["Pre_User_Profile"] = data
        return JsonResponse({"Profile": "Request Sent", "redirect_url": "/authentication/profile/" }, status=200)    
    return JsonResponse({"error": "Invalid request"}, status=400)
    
def authentication_profile(request):
    user_data = request.session.get("Pre_User_Profile", {})
    context ={
        "UserPreData": user_data
    }
    return render(request,'main/authentication/auth_registrationProfile.html', context)

def authentication_ADD(request):
    if(request.method =="POST"):
        get_image_file = request.FILES.get("ImageFile")
        bio = request.POST.get("bio")
        get_user_data = json.loads(request.POST.get('UserDataPrep'))
        u = UserSites()
        #lastID = UserSites.objects.values('ID').last()
        #u.ID = lastID['ID'] + 1
        u.first_name = get_user_data['firstName']
        u.last_name = get_user_data['lastName']
        u.email = get_user_data['email']
        u.password = get_user_data['password']
        u.profile_picture = get_image_file
        u.city_or_municipality = get_user_data['municipality_or_city']
        u.username = get_user_data['username']
        u.subdivision = get_user_data['subdivision']
        u.bio = bio
        u.save()           
        # Check if data pass server
        """        
        print(get_image_file)
        print(get_user_data)
        print(bio)
        """
        
        return JsonResponse({"msg": "New user created complete."
        ""}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)

def authentication_logout(request):
    logout(request)
    return redirect("/authentication/login/")

# DIY CONNECT APP

def home(request):
   
    get_role_post_filter = request.session.get("RolesPostFilter", "Innovator")
    if request.user.is_authenticated:
        get_username = request.user.username
    else:
        get_username = "guest"
    context ={"username": get_username,"role_post_filter":get_role_post_filter}
    return render(request,'main/diyconn/home.html', context)

# POST
@login_required
def postLikeAdd(request):
    if(request.method =="POST"):
        data = json.loads(request.body)
        print(data)
        get_userPost= UserPost.objects.get(ID=data['post_id'])
        p = PostLike()
        p.user =request.user
        p.post = get_userPost
        p.save()
        
       
        
        return JsonResponse({"msg": "Liked Post"}, status=200)
        

@login_required
def postLikeRemoved(request):
    data = json.loads(request.body)
    print(data)
    get_userPost= UserPost.objects.get(ID=data['post_id'])
    get_likePost = PostLike.objects.get(post = get_userPost, user =request.user)
    get_likePost.delete()
    print("removed liked")
    return JsonResponse({"msg": "Liked Post"}, status=200)
def postGet_specific(request,post_id):
     post = UserPost.objects.filter(ID=post_id).first()
     get_post_blobs = UserPost_BLOB.objects.filter(USER_POST_ID=post)
     #print(get_post_blobs)
     if post is None:
         post = False
     context={"post_data":post,
              "post_data_blob":get_post_blobs,
              }
     return render(request,'main/subpages/post/postRetrieve.html', context)


def postGet_profile(request, username):
   
    check_owner_user = False
    user_profile = UserSites.objects.get(username=username)
    user_list_post = UserPost.objects.filter(USER_ID = user_profile).order_by('-modified_at')
    if(request.user==user_profile):
        check_owner_user =True
    context = []
    for post in user_list_post:
            blobs = UserPost_BLOB.objects.filter(USER_POST_ID=post).order_by('position')
            blob_list = [
                {
                    "id": blob.ID,
                    "image_url": blob.blob.url,
                    "position": blob.position
                }
                for blob in blobs
            ]

            context.append({
                "id": post.ID,
                "username":post.USER_ID.username,
                "user_location":{"subdivision": post.USER_ID.subdivision,"city_or_municipality":post.USER_ID.city_or_municipality},
                "title": post.title, 
                "description": post.description,  
                "date_modified": post.modified_at,
                "blobs": blob_list,
                "user_ID":post.USER_ID.ID,
                "check_owner_user":check_owner_user               
            })

    
    
    return JsonResponse({"msg": "Checking if there is a post", "items":context}, status=200)


def postRoleChange(request):
    if(request.method =="POST"):
        data = json.loads(request.body)
        request.session["RolesPostFilter"] = data['role']
      
        return JsonResponse({"msg": "Changing Item Post"}, status=200)


def postGet(request,lastest_post, role_post):
    timeout = 30
    start_time = time.time()
    # = UserPost.objects.filter(user_role_type = role_post )
   
    while time.time() - start_time < timeout:
            try:
                new_posts = UserPost.objects.filter(user_role_type=role_post).order_by("-modified_at")[lastest_post]

                if new_posts:
                    total_likes =0
                    lastest_post +=1  # Update latest post ID
                    get_blob_info  = UserPost_BLOB.objects.filter(USER_POST_ID = new_posts).order_by('position')
                    item = get_blob_info.first().blob.url
                    print(request)
                    get_likes_filter = PostLike.objects.filter(post =new_posts)
                  
                    if request.user.is_authenticated:
                        already_liked = PostLike.objects.filter(post=new_posts, user=request.user).exists()
                       
                    else:
                        already_liked = "guest"
                    for like in get_likes_filter:
                        total_likes+=1
                    return JsonResponse({
                'new_posts':{
                    'id': new_posts.ID,
                    'title': new_posts.title,
                    'description':new_posts.description,
                    'date_modified': new_posts.modified_at,
                    'user': new_posts.USER_ID.ID, 
                    'username': new_posts.USER_ID.username,
                    'user_location':{'subdivision':new_posts.USER_ID.subdivision, 'city_or_municipality': new_posts.USER_ID.city_or_municipality}, 
                    'profile_urls': new_posts.USER_ID.profile_picture.url if new_posts.USER_ID.profile_picture else None,

                    'blob_url': [item.blob.url for item in get_blob_info],
                    "role_post":role_post,
                    "like": total_likes,
                    "already_liked":already_liked,
                   "ownership_post": new_posts.USER_ID == request.user

                  
                    
                    
                },  # Convert queryset to list
                'latest_post_count': lastest_post
            })
         
                time.sleep(2)

            except:
                return JsonResponse({"msg": "There is no new post available"}, status=500)


@login_required
def postAdd(request):

    if(request.method =="POST"):
       
        role = request.POST.get("role")
        title = request.POST.get("title")
        description = request.POST.get("description")

        # Retrieve multiple files
        
        images_files = request.FILES.getlist("imagesFiles[]")
        up = UserPost()
       
        """
        #DEBUGGING
        print(request.FILES)
        print("Role:", role)
        print("Title:", title)
        """
        up.USER_ID = request.user
        up.description = description
        up.title = title
        up.user_role_type = role
        up.save()
        lastID = UserPost.objects.values('ID').last()
        last_obj_up =  UserPost.objects.get(ID = lastID['ID'])
        i =0
        """
        # DEBUGGING
        print(lastID)
        print(last_obj_up)
        images_files = []
        """
        for key in request.FILES:
            if key.startswith("imagesFiles["):  # Match keys like 'imagesFiles[0]', 'imagesFiles[1]'
              
                
                file = request.FILES[key]
                saved_image = UserPost_BLOB.objects.create(
                USER_POST_ID=last_obj_up,
                position=i,
                blob=file)
                i+=1
                # images_files.append(request.FILES[key])  # -- Checking Info     
        
       
        #print("Uploaded Files:", [file.name for file in images_files]) # -- Checking Info
       

        
        return JsonResponse({"msg": "Request Complete","redirect_url":"diyconnect/home/"}, status=200)
    context ={}
    return render(request,'main/subpages/post/postAdd.html', context)

def postSearch(request, search_item):
    #print(search_item)
    get_innovator = UserPost.objects.filter(title__icontains=search_item, user_role_type ="Innovator")
    get_contributor = UserPost.objects.filter(title__icontains=search_item, user_role_type ="Contributor")
    get_collector = UserPost.objects.filter(title__icontains=search_item, user_role_type ="Collector")
    get_users = UserSites.objects.filter(username__icontains=search_item)
    
    # Testing

    """
    print("Innovator")
    print(get_innovator)
    print("Contributor")
    print(get_contributor)
    print("collector")
    print(get_collector)
    print("user")
    print(get_users)
    """
    context ={
     "Innovator_post":get_innovator,
     "Contributor_post":get_contributor,
     "Collector_post":get_collector,
     "search_item": search_item,
     "user_profile": get_users
    }
    return render(request,'main/subpages/search/search.html', context)

@login_required
def postDelete(request, post_id):
    #print("this is for delete post")
    get_post = UserPost.objects.get(ID = post_id)
    get_post.delete()
    return JsonResponse({"msg": "Deleting Post", "redirect_url":"/diyconnect/home/"}, status=200)

@login_required
def postEdit(request, post_id):


    get_post = UserPost.objects.get(ID=post_id)
    get_username = get_post.USER_ID.username
    get_post_blobs = UserPost_BLOB.objects.filter(USER_POST_ID=get_post)
    context ={
    "post_data":get_post,
     "post_data_blob":get_post_blobs,
     "prev_url_location": f"/diyconn/profile/get/{get_username}"
    }
    return render(request,'main/subpages/post/postEdit.html',context)

@login_required
def postEditSave(request, post_id):
    if(request.method=="POST"):
       
        get_post = UserPost.objects.get(ID=post_id)

        role = request.POST.get("role")
        title = request.POST.get("title")
        description = request.POST.get("description")
        get_post.description=description
        get_post.user_role_type =role
        get_post.title = title
        get_post.save()
        if not request.FILES:
            
            return JsonResponse({"msg": "Saving Modifying Post (no images)", "redirect_url": "/diyconnect/home/"}, status=200)

        #print("FILES RECEIVED:", request.FILES)

        # Optional: delete previous blobs
        UserPost_BLOB.objects.filter(USER_POST_ID=get_post).delete()

        i = 0
        for key in request.FILES:
            if key.startswith("imagesFiles["):
                file = request.FILES[key]
                UserPost_BLOB.objects.create(
                    USER_POST_ID=get_post,
                    position=i,
                    blob=file
                )
                i += 1

        return JsonResponse({"msg": "Saving Modifying Post (with images)", "redirect_url": "/diyconnect/home/"}, status=200)


#messages
@login_required
def MessageMobile(request):
    context= {}
    
    return render(request, 'main/subpages/messages/mobile-conversations/mobile-conversation.html',context)
@login_required
def MessageMobileConversationContent(request, user_id):
    request.session["selectedMessage"] =user_id
    selected_message = request.session.get("selectedMessage")
    u = UserSites.objects.get(ID=user_id)
    
    context ={
        "user":u,
        "selected_messages":selected_message,
        
    }
    return render(request, 'main/subpages/messages/mobile-conversations/mobile-conversation-content.html',context)


@login_required
def Messages(request):
    data_user_id = request.session.get("selectedMessage")
    if(request.method =="POST"):
        data = json.loads(request.body)
       

    context ={"id":data_user_id}
    return render(request, 'main/subpages/messages/messages.html',context)

@login_required
def MessagesGet(request):
    selected_message = request.session.get("selectedMessage")
    if(request.method=="POST"):
        """
        context =[]
        earliest = UserMessages.objects.filter(
    USER_SENDER_ID=request.user,
    USER_RECIPIENT_ID=OuterRef('USER_RECIPIENT_ID')
).order_by('created_at')
     
        messages_owner = UserMessages.objects.filter(
    USER_SENDER_ID=request.user,
    created_at=Subquery(earliest.values('created_at')[:1])
)
        earliest2 = UserMessages.objects.filter(
    USER_SENDER_ID=OuterRef('USER_SENDER_ID'),
    USER_RECIPIENT_ID=request.user
).order_by('created_at')
     
        messages_owner2 = UserMessages.objects.filter(
    USER_RECIPIENT_ID=request.user,
    created_at=Subquery(earliest2.values('created_at')[:1])
)
       #messages_owner= UserMessages.objects.filter(USER_SENDER_ID = request.user).order_by("created_at").distinct("USER_RECIPIENT_ID")
        print(messages_owner)
        for messages_own in messages_owner:
            context.append({
                "id": messages_own.ID,
                "created_at":messages_own.created_at,
                 "status":messages_own.status ,
                 "user_id":messages_own.USER_RECIPIENT_ID.ID,
                 "message_text": messages_own.message_text,
                 "username":messages_own.USER_RECIPIENT_ID.username,
                  "Profile": messages_own.USER_RECIPIENT_ID.profile_picture.url if messages_own.USER_RECIPIENT_ID.profile_picture else "",
            })

        for messages_own in messages_owner2:
            context.append({
                "id": messages_own.ID,
                "created_at":messages_own.created_at,
                 "status":messages_own.status ,
                 "user_id":messages_own.USER_SENDER_ID.ID,
                 "message_text": messages_own.message_text,
                 "username":messages_own.USER_SENDER_ID.username,
                  "Profile": messages_own.USER_SENDER_ID.profile_picture.url if messages_own.USER_SENDER_ID.profile_picture else "",
            })
        """

        user = request.user

        # Get distinct user IDs the current user has chatted with
        conversation_users = UserMessages.objects.filter(
            Q(USER_SENDER_ID=user) | Q(USER_RECIPIENT_ID=user)
        ).exclude(
            Q(USER_SENDER_ID=user, USER_RECIPIENT_ID=user)  # avoid self-conversations
        ).annotate(
            other_user_id=Case(
                When(USER_SENDER_ID=user, then=F('USER_RECIPIENT_ID')),
                default=F('USER_SENDER_ID'),
                output_field=models.IntegerField()
            )
        ).values('other_user_id').distinct()

        # Now get latest message per each "other user"
        context = []
        
        for row in conversation_users:
            other_user_id = row['other_user_id']

            latest_msg = UserMessages.objects.filter(
                Q(USER_SENDER_ID=user, USER_RECIPIENT_ID_id=other_user_id) |
                Q(USER_SENDER_ID_id=other_user_id, USER_RECIPIENT_ID=user)
            ).order_by('-created_at').first()

            other_user = latest_msg.USER_SENDER_ID if latest_msg.USER_SENDER_ID != user else latest_msg.USER_RECIPIENT_ID
            #print(f"ID {latest_msg.USER_SENDER_ID}. Target: {request.user.ID}")
            if(latest_msg.USER_SENDER_ID == request.user):
                position = "right"
            else:
                position= "left"
           
          
        


            context.append({
                "id": latest_msg.ID,
                "created_at": latest_msg.created_at,
                "status": latest_msg.status,
                "user_id": other_user.ID,
                "message_text": latest_msg.message_text,
                "username": other_user.username,
                "position_conversation": position,
                "Profile": other_user.profile_picture.url if other_user.profile_picture else "",
               
             
            })
        return JsonResponse({"msg": "Messages Data Retrieve Successfully","messages": context, "selected_message":selected_message}, status=200)

@login_required
def MessageConversationGet(request,sender_id):
    request.session["selectedMessage"] =sender_id
    if(request.method =="POST"):
     
        get_receiver = UserSites.objects.get(ID = sender_id)
        conversations = UserMessages.objects.filter(
        Q(USER_SENDER_ID=request.user, USER_RECIPIENT_ID=get_receiver, message_text__isnull=False) |
        Q(USER_SENDER_ID=get_receiver, USER_RECIPIENT_ID=request.user, message_text__isnull=False)
    ).order_by("created_at")
        context =[]
    
        if(not conversations):
    
            return JsonResponse({"msg": "Messages Data Retrieve Successfully","messages": context}, status=200)
        for conversation in conversations:
            if(conversation.USER_SENDER_ID ==get_receiver):
                position = "left"

            else:
                position = "right"
            details = None
            if(conversation.status==MessageStatus.REQUEST or conversation.status== MessageStatus.CANCELLED or conversation.status== MessageStatus.FULFILLED):

                get_blob_details = conversation.message_text
                post_id_str = get_blob_details.split(" - ")[0]
                details = UserPost.objects.filter(ID=post_id_str).first()
              
            context.append({
                        "id": conversation.ID,
                        "created_at":conversation.created_at,
                        "status":conversation.status ,
                        "message_text": conversation.message_text,
                        # For Checking purposes must be removed when developement
                        "username":conversation.USER_RECIPIENT_ID.username,
                        "position_conversation": position,
                           "blob_details": {
                    "id": details.ID,
                    "title": details.title
                }if details else None
                        })

        return JsonResponse({"msg": "Messages Data Retrieve Successfully","messages": context, "conversation_username":get_receiver.username}, status=200)
        

def MessageConvesationAdd(request, receiver_id):
    if(request.method =="POST"):
        request.session["selectedMessage"] = receiver_id
        lastID =UserMessages.objects.values('ID').last()
        data = json.loads(request.body)

        sender = UserSites.objects.get(ID=request.user.ID)
        reciever = UserSites.objects.get(ID=receiver_id)
        messages = UserMessages()
        messages.ID = lastID['ID'] + 1
        messages.USER_SENDER_ID = sender
        messages.USER_RECIPIENT_ID = reciever
        messages.message_text =data['message']
        messages.save()

        n =Notification()
        n.USER_NOTIFY_OWNER = reciever
        n.USER_NOTIFY_TRIGGER = sender
        n.type = NotifyType.MESSAGE
        n.save()
        return JsonResponse({"msg": "Messages Data Retrieve Successfully"}, status=200)
        


def MessageAdd(request, receiver_id):
    if(request.method =="POST"):
        get_receiver = UserSites.objects.get(ID = receiver_id)

        check_exist_conversation = UserMessages.objects.filter(
    Q(USER_SENDER_ID=request.user, USER_RECIPIENT_ID=get_receiver, message_text__isnull=False) |
    Q(USER_SENDER_ID=get_receiver, USER_RECIPIENT_ID=request.user, message_text__isnull=False)
).order_by("created_at")
        if(not check_exist_conversation): 
            u = UserMessages()
            u.USER_SENDER_ID = request.user
            u.USER_RECIPIENT_ID = get_receiver
            u.message_text = None
            u.save()
        #context =[]
        return JsonResponse({"msg": "Messages created successfully", "redirect_url":"/diyconn/messages/"}, status=200)


#Message Request
def MessageAddRequest(request,receiver_id):
       
    try: 

        if(request.method =="POST"):
            
            get_receiver = UserSites.objects.get(ID = receiver_id)
            data = json.loads(request.body)
            post_id = data["post_id"]
            get_post_data = UserPost.objects.filter(ID= post_id).first()

            check_request_pending = TaskRequest.objects.filter(USER_FULLFILL_REQUEST = request.user,USER_RECIEVE_REQUEST=get_receiver,POST_ID=get_post_data).first()
            print(data)
            print(check_request_pending)
  
            if check_request_pending==None:
                
                u = UserMessages()
                u.USER_SENDER_ID = request.user
                u.USER_RECIPIENT_ID = get_receiver
                u.message_text = f'{get_post_data.ID} - {get_post_data.title}'
                u.status ="request"
                u.save()
                lastID = UserMessages.objects.values('ID').last()

                
                t = TaskRequest()
                t.POST_ID = get_post_data
                t.USER_FULLFILL_REQUEST = request.user
                t.USER_RECIEVE_REQUEST =  get_receiver
                t.accepted = True
                t.conversation_id = lastID["ID"]
                t.save()
                #print("working")

                #NOTIFICATION
                n=Notification()
                n.USER_NOTIFY_OWNER = get_receiver
                n.USER_NOTIFY_TRIGGER= request.user
                n.type = NotifyType.REQUEST
                n.save()
                return JsonResponse({"msg": "Request Added"}, status=200)
            else:
               
                return JsonResponse({"msg": "Request is existed"}, status=200)
          
            # For Message
            
         
            # For Request 
        
                
            
    except:
        return JsonResponse({"msg": "Request Error"}, status=500)

#people
@login_required
def people(request):
    context ={}
    return render(request,'main/subpages/people/people.html', context)
def peopleFriendRequest_get(request):
    context =[]
    received_request = Friendships.objects.filter(RECEIVER_ID=request.user, status ='pending')
    for user in received_request:
        context.append({
                "id": user.REQUESTER_ID.ID,
                "username":user.REQUESTER_ID.username,
                 "Profile": user.REQUESTER_ID.profile_picture.url if user.REQUESTER_ID.profile_picture else "",
                 "status": user.status,
             
            })
    
    return JsonResponse({"msg": "Friend request sent successfully", "FriendRequest": context}, status=200)

@login_required
def peopleFriendRequest_accepted(request, user_id):
  
    requester_user = UserSites.objects.get(ID=user_id)
    accept_request= Friendships.objects.get(RECEIVER_ID =request.user, REQUESTER_ID =requester_user)
    accept_request.status ="accepted" 
    accept_request.save()

    n = Notification()
    n.USER_NOTIFY_OWNER = requester_user
    n.USER_NOTIFY_TRIGGER = request.user
    n.type = NotifyType.ACCEPT_FRIEND
    n.save() 

    return JsonResponse({"msg": "This is for friend request accepted"}, status=200)

@login_required
def peopleFriendRequest_pending(request, user_id):
    requester_user = UserSites.objects.get(ID=user_id)
    reject_request= Friendships.objects.get(RECEIVER_ID =request.user, REQUESTER_ID =requester_user)
    reject_request.status ="pending"
 
    reject_request.save()
    remove_notification = Notification.objects.filter(    Q(USER_NOTIFY_OWNER=request.user, USER_NOTIFY_TRIGGER=reject_request) | Q(USER_NOTIFY_OWNER=reject_request, USER_NOTIFY_TRIGGER=request.user), type =NotifyType.ACCEPT_FRIEND).first()
    remove_notification.delete()
    return JsonResponse({"msg": "This is for friend request rejected"}, status=200)


@login_required
def peopleGetDiscover(request):
    try:
        users = UserSites.objects.exclude(ID = request.user.ID).order_by(Random())
        context =[]
        for user in users:
            get_not_friends = Friendships.objects.filter(    Q(REQUESTER_ID=request.user, RECEIVER_ID=user) | Q(REQUESTER_ID=user, RECEIVER_ID=request.user)).first()
            if get_not_friends is None:
                    context.append({
                    "id": user.ID,
                    "username":user.username,
                        "Profile": user.profile_picture.url if user.profile_picture else ""
                    
                })
                    if(len(context)>=5):
                        break

       
        return JsonResponse({"msg": "Discover friends list retrieved successfully.","DiscoverPeople": context}, status=200)
    except Exception as e:
        return JsonResponse({"msg": "An error occurred while retrieving the people to discover"}, status=500)


@login_required
def peopleAdd(request, user_id):
    try:

        if(request.method =="POST"):
            getUser_requester_request = request.user
            getUser_receiver_request = UserSites.objects.get(ID=user_id)
            #print(f'${getUser_receiver_request}, {getUser_requester_request}')
            f = Friendships()
            f.RECEIVER_ID = getUser_receiver_request
            f.REQUESTER_ID = getUser_requester_request
            f.save()
            n = Notification()
            n.USER_NOTIFY_OWNER = getUser_receiver_request
            n.USER_NOTIFY_TRIGGER =getUser_requester_request
            n.type = NotifyType.ADD_FRIEND
            n.save()
            return JsonResponse({"msg": "Friend request sent successfully."}, status=200)
        else:
            return JsonResponse({"msg": "Invalid request method."}, status=500)
    except Exception as e:
        #print(f"Error in add_friend_request: {e}")  # helpful for debugging
        return JsonResponse({"msg": "An error occurred while sending the friend request."}, status=500)

@login_required
def peopleDelete(request, user_id):
    #try:
        if(request.method =="POST"):
            remove_friend_request = Friendships.objects.filter(    Q(REQUESTER_ID=request.user, RECEIVER_ID=user_id) | Q(REQUESTER_ID=user_id, RECEIVER_ID=request.user)).first()
            Notification.objects.filter(Q(USER_NOTIFY_OWNER=request.user, USER_NOTIFY_TRIGGER=user_id) | Q(USER_NOTIFY_OWNER=user_id, USER_NOTIFY_TRIGGER=request.user),type=NotifyType.ACCEPT_FRIEND).delete()

            remove_friend_request.delete()
            #print("this is for delete method")
            return JsonResponse({"msg": "Friend removed successfully."}, status=200)
        else:
            return JsonResponse({"msg": "Invalid request method."}, status=500)
    #except Exception as e:
        #print(f"Error in add_delete_friend_request: {e}")  # helpful for debugging
        #return JsonResponse({"msg": "An error occurred while delete the friend status."}, status=500)

@login_required
def peopleFriends(request):
    
    if(request.method =="POST"):
        context =[]
        friends_list = Friendships.objects.filter(status="accepted").filter(Q(REQUESTER_ID=request.user) | Q(RECEIVER_ID=request.user))
        
    
        if not friends_list.exists():
            friends_list = None  # or [] if you prefer an empty list
        else:
            friends_profiles = []
            for friendship in friends_list:
                if friendship.REQUESTER_ID == request.user:
                    friends_profiles.append(friendship.RECEIVER_ID.ID)
                else:
                    friends_profiles.append(friendship.REQUESTER_ID.ID)
            for data in friends_profiles:
                user = UserSites.objects.get(ID = data)
                context.append({
                "id": user.ID,
                "username":user.username,
                 "Profile": user.profile_picture.url if user.profile_picture else ""
             
            })
        #print("this is for people Friends")
        return JsonResponse({"msg": "Friends list retrieved successfully.","FriendList": context}, status=200)

@login_required
def profile_user(request, username):
    check_owner_post = False
    get_user_id=''
   

    user_details = UserSites.objects.get(username=username)
    get_user_number_post_contributor = UserPost.objects.filter(USER_ID=user_details, user_role_type ="Contributor").count()
    get_user_number_post_innovator = UserPost.objects.filter(USER_ID=user_details, user_role_type ="Innovator").count()
    get_user_number_post_collector = UserPost.objects.filter(USER_ID=user_details, user_role_type ="Collector").count()
    chk_admin = False
    if(user_details.is_superuser):
        chk_admin =True
    else:
        chk_admin = False
    avg_rating_contributor = avg_rating_collector = avg_rating_innovator=0
    arr_avg_contributor, arr_avg_collector, arr_avg_innovator = [], [], []
    get_reviews = Review.objects.filter(USER_FULLFILL_REQUEST = user_details)
    user = UserSites.objects.get(username=username)
    friend_status = ""
    get_friendship = Friendships.objects.filter(    Q(REQUESTER_ID=request.user, RECEIVER_ID=user) | Q(REQUESTER_ID=user, RECEIVER_ID=request.user)).first()
  
    if(request.user==user):
        friend_status="user_owner"
        #print("same_value")
    elif(get_friendship ==None):
        friend_status="no_relationship"
        #print("no realtionsship")
    elif(get_friendship.status == FriendStatus.ACCEPTED):
        friend_status="accepted"
        #print("FriendACCEPTED")
    elif(get_friendship.status ==FriendStatus.PENDING and get_friendship.REQUESTER_ID ==request.user):
        friend_status ="pending"
        #print("Waiting to accept")
    elif(get_friendship.status == FriendStatus.PENDING and get_friendship.RECEIVER_ID):
        friend_status ="accept_request"
        #print("you can accept his friend request")
    
    for review in get_reviews:
      
        u = UserPost.objects.get(title= review.post_title)
        #print(u.user_role_type)
        if(u.user_role_type == "Contributor"):
            arr_avg_contributor.append(review.stars)
        elif(u.user_role_type == "Collector"):
            arr_avg_collector.append(review.stars)
        elif(u.user_role_type == "innovator"):
            arr_avg_innovator.append(review.stars)
    
    avg_rating_contributor = sum(arr_avg_contributor) / len(arr_avg_contributor) if arr_avg_contributor else 0
    avg_rating_collector = sum(arr_avg_collector) / len(arr_avg_collector) if arr_avg_collector else 0
    avg_rating_innovator = sum(arr_avg_innovator) / len(arr_avg_innovator) if arr_avg_innovator else 0

   
        
    if(request.user.username == username):
        check_owner_post= True
        get_user_id = request.user.ID
    else:
        get_user = UserSites.objects.filter(username=username).first()
        get_user_id = get_user.ID
    
    context ={
        "username":username,
        "Check_owner_post":check_owner_post,
        "get_id_user":get_user_id,
        "user_details":user_details,
        "number_post_contributor":get_user_number_post_contributor,
        "number_post_innovator":get_user_number_post_innovator,
        "number_post_collector":get_user_number_post_collector,
        "avg_rating_contributor": round(avg_rating_contributor),
        "avg_rating_collector": round(avg_rating_collector),
        "avg_rating_innovator":round(avg_rating_innovator),
        "friend_status":friend_status,
        "check_admin": chk_admin,

    }
    return render(request,'main/subpages/profile/profileView.html', context)


#TASKREQUEST
@login_required
def request_fulfiller_cancelled(request):
    if(request.method =="POST"):
        try:
            data = json.loads(request.body)
            get_taskRequest =TaskRequest.objects.get(POST_ID=data['post_id'],conversation_id =data['conversation_id'])
            get_notify_owner = UserSites.objects.get(ID=get_taskRequest.POST_ID.USER_ID.ID)
            get_conversation = UserMessages.objects.get(ID=data['conversation_id'])
            get_conversation.status = MessageStatus.CANCELLED
            get_conversation.save()
            get_taskRequest.delete()
            
            #notification
            n =Notification()
            n.USER_NOTIFY_OWNER = get_notify_owner
            n.USER_NOTIFY_TRIGGER= request.user
            n.type = NotifyType.CANCELLED
            n.save()
            return JsonResponse({"msg": "Fulfilling Request Cancelled"}, status=200)
        except:
            return JsonResponse({"msg": "Internal Error"}, status=500)



# ADDED REVIEW AND REQUEST COMPLETED
@login_required
def request_receiver_completed(request):
    if(request.method =="POST"):
    
        data = json.loads(request.body)
        print(data)
    
        get_taskRequest =TaskRequest.objects.get(POST_ID=data['post_id'],conversation_id =data['conversation_id'])
        get_conversation = UserMessages.objects.get(ID=data['conversation_id'])
  
        get_taskRequest.accepted =True
        get_taskRequest.completed=True
        get_owner =UserSites.objects.get(ID =get_taskRequest.USER_FULLFILL_REQUEST.ID)
        n =Notification()
        n.USER_NOTIFY_OWNER = get_owner
        n.USER_NOTIFY_TRIGGER= request.user
        n.type =NotifyType.FULFILLED
        n.save()
        r = Review()
        r.post_title =get_taskRequest.POST_ID.title
        r.USER_FULLFILL_REQUEST= get_taskRequest.USER_FULLFILL_REQUEST
        r.USER_RECIEVE_REQUEST= request.user
        r.stars = data['rate']
        r.comment =data['comment']
        
        get_conversation.status =MessageStatus.FULFILLED

        print("this is complete request")
        r.save()
        get_conversation.save() 
        get_taskRequest.save()
        return JsonResponse({"msg": "Request Task Has been Fulfilled"}, status=200)




#Reviews
@login_required
def reviews(request, user_id):
    context ={}
    get_user = UserSites.objects.get(ID = user_id)
    get_reviews_user = Review.objects.filter(USER_FULLFILL_REQUEST = get_user)
    print(get_reviews_user)
    context ={
    "user": get_user,
    "reviews": get_reviews_user
    }
    print("this is for review")
    return render(request,'main/subpages/reviews/review.html', context)

#Settings
@login_required
def setting(request):

    get_user= UserSites.objects.get(ID=request.user.ID)
    print("setting")
    context ={"user":get_user}
    return render(request,'main/subpages/settings/setting.html', context)

@login_required
def setting_verify_password(request):
    data = json.loads(request.body)
    get_owner = UserSites.objects.get(ID= request.user.ID)
    test_password =get_owner.check_password(data['verify_password'])
 
    if test_password == True:
          return JsonResponse({"msg": "Verify password correct"}, status=200)
    else:
          return JsonResponse({"msg": "Verify password wrong"}, status=500)
    

@login_required
def setting_save_changes(request):
    print("save_changes")
    changed = False
    get_user = UserSites.objects.get(ID=request.user.ID)
    new_password = request.POST.get("inp_new_password")
    subdivision = request.POST.get("inp_subdivision")
    image_file = request.FILES.get("inp_image_prof")
    bio  = request.POST.get("inp_bio")

    
    if(new_password !=None and new_password!=""):
        get_user.password = new_password
        changed = True
    if(subdivision !=None and subdivision!=""):
        get_user.subdivision = subdivision
        changed = True
    if(image_file !=None and image_file!=""):
        changed = True
        get_user.profile_picture = image_file
    if(bio !=None and bio!=""):
        get_user.bio = bio
    if (new_password !=None and new_password!="" and changed==True):
        get_user.save()
        logout(request)
        return JsonResponse({"msg": "Verify password correct","redirect_url":"/authentication/login/"}, status=200)
    if changed:
        get_user.save()

    return JsonResponse({"msg": "Verify password correct","redirect_url":"/diyconn/setting/"}, status=200)


#notification
@login_required
def notification(request):
    get_notification = Notification.objects.filter(USER_NOTIFY_OWNER=request.user).order_by("-created_at")
    print("notification")
    for notif in get_notification:
        print(notif.type)
    context={"notifications":get_notification}
    return render(request,'main/subpages/notification/notification.html', context)

@login_required
def notification_viewed(request, notif_id):
    print(notif_id)
    if request.method =="POST":
        get_notif_obj = Notification.objects.get(ID=notif_id)
        get_notif_obj.status =NotifyStatus.VIEWED
        get_notif_obj.save()
        print("viewed")
        return JsonResponse({"msg": "Notification Viewed"}, status=200)
    


def changeNewpassword(request):
    data = json.loads(request.body)
    getUser= UserSites.objects.filter(email =data["user_email"]).first()
    length =7
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    result = ''.join(random.choice(characters) for _ in range(length))
    print(getUser.username)


    
    if getUser:
    
        f = FogotPasswordFixed()
        f.REFENCE_USER = getUser
        f.new_password_change = result
        getUser.password = result
        print(result)
        f.save()
        getUser.save()
      
        return JsonResponse({"msg": "Changed password success"}, status=200)
    else:
        return JsonResponse({"msg": "Internal error can't change password"}, status=500)
    
@login_required
def user_feedback(request):
    data = json.loads(request.body)
    print(data)
    print("user feedback")

    if request.method =="POST":
        f = Feedback()
        f.username = data['username']
        f.feedback_msg = data['feedback']
        f.rate = data['rating']
        f.save()
        return JsonResponse({"msg": "Create a feedback"}, status=200)
    else:
        return JsonResponse({"msg": "Internal error can't create feedback"}, status=500)
#admin

def superuser_required(user):
    return user.is_superuser

@user_passes_test(superuser_required)
@login_required
def admin_forgotPassword(request):
    
    get_all = FogotPasswordFixed.objects.all().order_by("created_at")
    context={
        "data": get_all
    }
    print("Your")
    return render(request,'main/admin_temp/admin_forgot_password.html', context)


@user_passes_test(superuser_required)
@login_required
def admin_dashboard(request):
    context={    
    }
    print("dashboard")
    return render(request,'main/admin_temp/admin_dashboard.html', context)

@user_passes_test(superuser_required)
@login_required
def admin_checkUserpostDetails(request):
    post_details =[]
    get_all_userpost = UserPost.objects.all().order_by("modified_at")
    for userPost in get_all_userpost:
        up_b= UserPost_BLOB.objects.filter(USER_POST_ID=userPost.ID).order_by("-position")
        post_details.append({
            'post':userPost,
            'blob':up_b
        })
        #print(post_details)
    context ={
        'post_details':post_details
    }
    return render(request,'main/admin_temp/admin_postDetails.html', context)

@user_passes_test(superuser_required)
@login_required
def admin_deletePostDetails(request,post_id):
    if(request.method =="POST"):
        u = UserPost.objects.get(ID=post_id)
        u.delete()
        print("this is delete post")
        return JsonResponse({"msg": "Deleting Post"}, status=200)
    else:
        return JsonResponse({"msg": "Issue on deleting"}, status=200)


@user_passes_test(superuser_required)
@login_required    
def admin_CheckUsers(request):
    get_user = UserSites.objects.all().order_by("username")
    context ={

        "users":get_user
    }
    return render(request,'main/admin_temp/admin_checkUsers.html', context)

@user_passes_test(superuser_required)
@login_required
def admin_deleteUser(request, user_id):
    if request.method =="POST":
        getUser = UserSites.objects.get(ID=user_id)
        getUser.delete()
        print("this is delete user")
        return JsonResponse({"msg": "The user has been deleted"}, status=200)
    else:
        return JsonResponse({"msg": "There is an issue deleting a user"}, status=500)


@user_passes_test(superuser_required)
@login_required
def admin_feedbackCheck(request):
    f = Feedback.objects.all().order_by("-created_at")
    print(f)
    context ={
        "feedbacks": f
      
    }
    return render(request,'main/admin_temp/admin_feedback_check.html', context)



def custom_404_view(request, exception=None):
    return render(request, "main/404.html", status=404)