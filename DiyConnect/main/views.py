from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import check_password
from .models import UserSites, UserPost, UserPost_BLOB, Friendships, UserMessages, MessageStatus,TaskRequest,Review
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
import time
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models.functions import Random
from django.db.models import Q, Max, OuterRef, Subquery, F,Case, When,Exists
from django.db import models


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
@login_required
def home(request):
   
    get_role_post_filter = request.session.get("RolesPostFilter")
    get_username = request.user.username
    
    context ={"username": get_username,"role_post_filter":get_role_post_filter}
    return render(request,'main/diyconn/home.html', context)

# POST
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
   

    user_profile = UserSites.objects.get(username=username)
    user_list_post = UserPost.objects.filter(USER_ID = user_profile).order_by('-modified_at')
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
                    lastest_post +=1  # Update latest post ID
                    get_blob_info  = UserPost_BLOB.objects.filter(USER_POST_ID = new_posts).order_by('position')
                    item = get_blob_info.first().blob.url
                 
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


def postDelete(request, post_id):
    #print("this is for delete post")
    get_post = UserPost.objects.get(ID = post_id)
    get_post.delete()
    return JsonResponse({"msg": "Deleting Post", "redirect_url":"/diyconnect/home/"}, status=200)


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
def MessageMobile(request):
    context= {}
    
    return render(request, 'main/subpages/messages/mobile-conversations/mobile-conversation.html',context)
@login_required
def MessageMobileConversationContent(request, user_id):
    u = UserSites.objects.get(ID=user_id)
    
    context ={
        "user":u
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
            #print(data)
            #print(check_request_pending)
  
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
                return JsonResponse({"msg": "Request Added"}, status=200)
            else:
               
                return JsonResponse({"msg": "Request is existed"}, status=200)
          
            # For Message
            
         
            # For Request 
        
                
            
    except:
        return JsonResponse({"msg": "Request Error"}, status=500)

#people
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

def peopleFriendRequest_accepted(request, user_id):
  
    requester_user = UserSites.objects.get(ID=user_id)
    accept_request= Friendships.objects.get(RECEIVER_ID =request.user, REQUESTER_ID =requester_user)
    accept_request.status ="accepted" 
    accept_request.save()

    return JsonResponse({"msg": "This is for friend request accepted"}, status=200)

def peopleFriendRequest_pending(request, user_id):
    requester_user = UserSites.objects.get(ID=user_id)
    reject_request= Friendships.objects.get(RECEIVER_ID =request.user, REQUESTER_ID =requester_user)
    reject_request.status ="pending" 
    reject_request.save()
    return JsonResponse({"msg": "This is for friend request rejected"}, status=200)


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
            return JsonResponse({"msg": "Friend request sent successfully."}, status=200)
        else:
            return JsonResponse({"msg": "Invalid request method."}, status=500)
    except Exception as e:
        #print(f"Error in add_friend_request: {e}")  # helpful for debugging
        return JsonResponse({"msg": "An error occurred while sending the friend request."}, status=500)

def peopleDelete(request, user_id):
    try:
        if(request.method =="POST"):
            remove_friend_request = Friendships.objects.filter(    Q(REQUESTER_ID=request.user, RECEIVER_ID=user_id) | Q(REQUESTER_ID=user_id, RECEIVER_ID=request.user)).first()
            remove_friend_request.delete()
            #print("this is for delete method")
            return JsonResponse({"msg": "Friend removed successfully."}, status=200)
        else:
            return JsonResponse({"msg": "Invalid request method."}, status=500)
    except Exception as e:
        #print(f"Error in add_delete_friend_request: {e}")  # helpful for debugging
        return JsonResponse({"msg": "An error occurred while delete the friend status."}, status=500)

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

def profile_user(request, username):
    check_owner_post = False
    get_user_id=''
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
    }
    return render(request,'main/subpages/profile/profileView.html', context)


#TASKREQUEST

def request_fulfiller_cancelled(request):
    if(request.method =="POST"):
        try:
            data = json.loads(request.body)
            get_taskRequest =TaskRequest.objects.get(POST_ID=data['post_id'],conversation_id =data['conversation_id'])
            get_conversation = UserMessages.objects.get(ID=data['conversation_id'])
            get_conversation.status = MessageStatus.CANCELLED
            get_conversation.save()
            get_taskRequest.delete()

            return JsonResponse({"msg": "Fulfilling Request Cancelled"}, status=200)
        except:
            return JsonResponse({"msg": "Internal Error"}, status=500)



# ADDED REVIEW AND REQUEST COMPLETED
def request_receiver_completed(request):
    if(request.method =="POST"):
    
        data = json.loads(request.body)
        print(data)
    
        get_taskRequest =TaskRequest.objects.get(POST_ID=data['post_id'],conversation_id =data['conversation_id'])
        get_conversation = UserMessages.objects.get(ID=data['conversation_id'])
  
        get_taskRequest.accepted =True
        get_taskRequest.completed=True
   
        
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