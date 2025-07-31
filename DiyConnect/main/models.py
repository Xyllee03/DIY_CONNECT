from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin

# test
class UserSiteRole(models.TextChoices):
    INNOVATOR = 'innovator', 'Innovator'
    CONTRIBUTOR = 'contributor', 'Contributor'
    COLLECTOR = 'collector', 'Collector'
    GUEST = 'guest', 'Guest'

class FriendStatus(models.TextChoices):
    PENDING= 'pending', 'Pending'
    ACCEPTED= 'accepted','Accepted'
    REJECTED = 'rejected','Rejected'
class MessageStatus(models.TextChoices):
    SENT= 'sent', 'Sent'
    DELIVERED= 'delivered','Delivered'
    SEEN = 'seen','Seen'
    REQUEST = 'request', 'Request'
    CANCELLED ='cancelled','Cancelled'
    FULFILLED= 'fulfilled','Fulfilled'



def user_profile_pic_path(instance, filename):
    return f'upload/profile_pic/{instance.username}/{filename}'


def user_post_blob_path(instance,filename):
    return f'upload/post/{instance.USER_POST_ID.USER_ID.username}/{filename}'
"""
class UserSite(models.Model):
    ID = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to=user_profile_pic_path)
    city_or_municipality = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserSiteRole.choices, default=UserSiteRole.CONTRIBUTOR)
    username = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    bio = models.CharField(max_length=250, null=True, blank=True)
    subdivision = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        # Hash the password before saving (only if it's not already hashed)
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"  
"""

class UserSiteManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # Hash password properly
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
     
        extra_fields.setdefault('is_staff', True)  # Ensure is_staff is True for superuser
        extra_fields.setdefault('is_superuser', True)  # Ensure is_superuser is True for superuser
        extra_fields.setdefault('is_active', True)  # Ensure is_active is True for superuser
        return self.create_user(username, password, **extra_fields)
       
    

class UserSites(AbstractBaseUser,PermissionsMixin,BaseUserManager):
    ID = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to=user_profile_pic_path)
    city_or_municipality = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserSiteRole.choices, default=UserSiteRole.CONTRIBUTOR)
    username = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    bio = models.CharField(max_length=250, null=True, blank=True)
    subdivision = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)  # Indicates whether the user can log in
    is_staff = models.BooleanField(default=False)  # Determines if the user can access the admin site
    is_superuser = models.BooleanField(default=False)  # If True, the user has all permissions
  
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='user_sites',  # Custom related_name to avoid the clash
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='user_sites_permissions',  # Custom related_name to avoid clash
        blank=True
    )

    # Add these fields

    
    objects = UserSiteManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    def save(self, *args, **kwargs):
        # Hash the password before saving (only if it's not already hashed)
        if not self.password.startswith('pbkdf2_sha256$'):
            #self.password = make_password(self.password)
            self.set_password(self.password) 
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"  
    

class UserPost(models.Model):
    ID = models.AutoField(primary_key=True)
    USER_ID = models.ForeignKey(UserSites,on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=530)
    title = models.CharField(max_length=120)
    share_url = models.CharField(max_length=250, blank=True, null=True)
    user_role_type = models.CharField(max_length=50)


class UserPost_BLOB(models.Model):
    ID = models.AutoField(primary_key=True)
    USER_POST_ID = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    blob = models.ImageField(upload_to=user_post_blob_path)
    position = models.IntegerField()



#Friends
class Friendships(models.Model):
    ID = models.AutoField(primary_key=True)
    REQUESTER_ID = models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='sent_requests')
    RECEIVER_ID = models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='received_requests')

    status = models.CharField(max_length=20, choices=FriendStatus.choices, default=FriendStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.REQUESTER_ID} → {self.RECEIVER_ID} ({self.status})"


# MESSAGES
class UserMessages(models.Model):
    ID = models.AutoField(primary_key=True)
    USER_SENDER_ID = models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='sent_messages')
    USER_RECIPIENT_ID = models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='received_messages')
    created_at= models.DateTimeField(auto_now_add=True)

    message_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.SENT)
  

    

#Request 

   

class TaskRequest(models.Model):
    ID= models.AutoField(primary_key=True)
    POST_ID= models.ForeignKey(UserPost,on_delete=models.CASCADE)
    USER_FULLFILL_REQUEST = models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='target_request_user')
    USER_RECIEVE_REQUEST= models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='fullfill_request_user')
    conversation_id= models.IntegerField()
    accepted = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)


class Review(models.Model):
    ID = models.AutoField(primary_key=True)
    post_title = models.TextField()
    USER_FULLFILL_REQUEST = models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='target_review_user')
    USER_RECIEVE_REQUEST= models.ForeignKey(UserSites, on_delete=models.CASCADE, related_name='fullfill_review_user')
    stars = models.IntegerField()
    comment = models.TextField()