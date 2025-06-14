

from django.urls import path,include

from .  import views

app_name ="main"
urlpatterns = [
    path('', views.index, name="index" ),
    path('authentication_base/', views.authentication_base, name="authentication_base" ),
    path('authentication/login/', views.authentication_login, name="authentication_login" ),
    path('authentication/registration/', views.authentication_registration, name="authentication_registration" ),
    path('authentication/profile/', views.authentication_profile, name="authentication_profile"),
     path('authentication/PreLoad/', views.authentication_preLoad, name="authentication_preLoad"),

     # CRUD OPERATION AUTHENTICATION
    path('authentication/ADD/', views.authentication_ADD, name="authentication_ADD"),
    path('authentication/logout/', views.authentication_logout, name ="authentication_logout"),

    # DIY CONNECT APP
    path('diyconnect/home/', views.home,  name="diyconn_home"),
    
    #People
 path('diyconnect/people/', views.people,  name="people"),
 path('diyconnect/people/friends', views.peopleFriends,  name="peopleFriends"),
 path('diyconnect/people/discover', views.peopleGetDiscover, name ='peopleGetDiscover'),
 path('diyconnect/people/friendRequest', views.peopleFriendRequest_get, name ='peopleFriendRequest_get'),
 path('diyconnect/people/friendRequest/accepted/<int:user_id>', views.peopleFriendRequest_accepted, name ='peopleFriendRequest_accepted'),
  path('diyconnect/people/friendRequest/pending/<int:user_id>', views.peopleFriendRequest_pending, name ='peopleFriendRequest_pending'),
 path('diyconnect/people/add/<int:user_id>', views.peopleAdd, name ='peopleAdd'),
 path('diyconnect/people/delete/<int:user_id>', views.peopleDelete, name ='peopleDelete'),
 
 
    #Search
    path('diyconnect/search/<str:search_item>', views.postSearch,  name="postSearch"),

    #POST
      path('post/getRoleChange/', views.postRoleChange,  name="postRoleChange"),
      path('post/add/', views.postAdd,  name="postAdd"),
            path('post/specific/<int:post_id>', views.postGet_specific,  name="postGet_specific"),
      path('post/edit/save/<int:post_id>', views.postEditSave,  name="postEditSave"),
      path('post/edit/<int:post_id>', views.postEdit,  name="postEdit"),
      path('post/get/<int:lastest_post>/<str:role_post>', views.postGet,  name="postGet"),
        path('post/delete/<int:post_id>/', views.postDelete,  name="postGet"),

      path('post/profile/get/<str:username>/', views.postGet_profile, name="postGet_profile"),
    #Messages
      path('diyconn/messages/', views.Messages,  name="Messages"),

  #Profile
    path('diyconn/profile/get/<str:username>/', views.profile_user, name ="profile_user"),
  

      #INITIALIZED
        path('Initialized/cookies/', views.set_csrf_token,  name="set_csrf_token"),
    
]
