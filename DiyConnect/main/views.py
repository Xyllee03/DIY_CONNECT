from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import check_password
from .models import UserSites, UserPost, UserPost_BLOB
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
import time
# Create your views here.


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
            #print(u_check)
          
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
        u = UserSites()
        #lastID = UserSites.objects.values('ID').last()
        #u.ID = lastID['ID'] + 1
        u.first_name = get_user_data['firstName']
        u.last_name = get_user_data['lastName']
        u.email = get_user_data['email']
        u.password_hash = get_user_data['password']
        u.profile_picture = get_image_file
        u.city_or_municipality = get_user_data['municipality_or_city']
        u.username = get_user_data['username']
        u.bio = bio
        u.save() 
           
        # Check if data pass server
        """        
        print(get_image_file)
        print(get_user_data)
        print(bio)
        """
        
        return JsonResponse({"msg": "Request Complete"}, status=200)

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
                print(new_posts)
        
                if new_posts:
                    lastest_post +=1  # Update latest post ID
                    get_blob_info  = UserPost_BLOB.objects.filter(USER_POST_ID = new_posts).order_by('position')
                    item = get_blob_info.first().blob.url
                    return JsonResponse({
                'new_posts':{
                    'id': new_posts.ID,
                    'title': new_posts.title,
                    'description':new_posts.description,
                                  
                    'blob_url': [item.blob.url for item in get_blob_info],
                    
                    
                },  # Convert queryset to list
                'latest_post_count': lastest_post
            })
                time.sleep(2)

            except:
                return JsonResponse({"msg": "There is no new post available"}, status=500)

# POST
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

    # Testing
    print("Innovator")
    print(get_innovator)
    print("Contributor")
    print(get_contributor)
    print("collector")
    print(get_collector)
    context ={
     "Innovator_post":get_innovator,
     "Contributor_post":get_contributor,
     "Collector_post":get_collector,
     "search_item": search_item
    }
    return render(request,'main/subpages/search/search.html', context)