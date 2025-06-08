from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import check_password
from .models import UserSites, UserPost, UserPost_BLOB, Friendships
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
import time
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models.functions import Random
from django.db.models import Q
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
        #print(data['username'])

        try:
            u_check = UserSites.objects.filter(username=data['username']).first()
            #print("this is login")
            #print(u_check)
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
                #print(request.user)
                #print(request.user.is_authenticated)
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
        #print(data)
        
        u_check = UserSites.objects.filter(username = data['username']).exists()
        if(u_check):
            return JsonResponse({"error": "The username has been used."}, status=400)
        
        request.session["Pre_User_Profile"] = data
        return JsonResponse({"Profile": "Request Sent", "redirect_url": "/authentication/profile/" }, status=200)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
    
def authentication_profile(request):
    #print("this is authentication profile")
    user_data = request.session.get("Pre_User_Profile", {})
   #print(user_data)
    context ={
        "UserPreData": user_data
    }
    return render(request,'main/authentication/auth_registrationProfile.html', context)



def authentication_ADD(request):
    if(request.method =="POST"):
        get_image_file = request.FILES.get("ImageFile")
        #get_user_data = request.POST.get("UserDataPrep")
        bio = request.POST.get("bio")
        get_user_data = json.loads(request.POST.get('UserDataPrep'))
        #print(get_user_data)
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
     print(get_post_blobs)
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
  
    #print(role_post)
    timeout = 30
    start_time = time.time()
    # = UserPost.objects.filter(user_role_type = role_post )
   
    while time.time() - start_time < timeout:
            try:
                new_posts = UserPost.objects.filter(user_role_type=role_post).order_by("-modified_at")[lastest_post]
                #print(new_posts)
        
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
        print(request.FILES)
        get_post = UserPost.objects.get(ID=post_id)

        role = request.POST.get("role")
        title = request.POST.get("title")
        description = request.POST.get("description")
        get_post.description=description
        get_post.user_role_type =role
        get_post.title = title
        get_post.save()
        if not request.FILES:
            print("There are no uploaded files")
            return JsonResponse({"msg": "Saving Modifying Post (no images)", "redirect_url": "/diyconnect/home/"}, status=200)

        print("FILES RECEIVED:", request.FILES)

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
def Messages(request):
    if(request.method =="POST"):
        data = json.loads(request.body)
        print(data)

    context ={}
    return render(request, 'main/subpages/messages/messages.html',context)


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
    #print("requestFriend")
    return JsonResponse({"msg": "Friend request sent successfully", "FriendRequest": context}, status=200)

def peopleFriendRequest_accepted(request, user_id):
    #print("this is friend request accepted")
    requester_user = UserSites.objects.get(ID=user_id)
    accept_request= Friendships.objects.get(RECEIVER_ID =request.user, REQUESTER_ID =requester_user)
    #print(accept_request)
    accept_request.status ="accepted" 
    accept_request.save()

    return JsonResponse({"msg": "This is for friend request accepted"}, status=200)

def peopleFriendRequest_pending(request, user_id):
    requester_user = UserSites.objects.get(ID=user_id)
    reject_request= Friendships.objects.get(RECEIVER_ID =request.user, REQUESTER_ID =requester_user)
    reject_request.status ="pending" 
    reject_request.save()
    #print("this is friend request rejected")
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

        #print(context)
        #print("this is for peopleget")
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
            #print("this is for people add")
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
        
        #print(friends_list)
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
    if(request.user.username == username):
        check_owner_post= True
    context ={
        "username":username,
        "Check_owner_post":check_owner_post,
    }
    return render(request,'main/subpages/profile/profileView.html', context)




