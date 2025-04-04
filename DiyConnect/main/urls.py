

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


    #Search
    path('diyconnect/search/<str:search_item>', views.postSearch,  name="postSearch"),

    #POST
      path('post/getRoleChange/', views.postRoleChange,  name="postRoleChange"),
      path('post/add/', views.postAdd,  name="postAdd"),
      path('post/get/<int:lastest_post>/<str:role_post>', views.postGet,  name="postGet"),


    
]
