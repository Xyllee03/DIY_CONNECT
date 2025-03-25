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

def user_profile_pic_path(instance, filename):
    return f'upload/post/{instance.username}/{filename}'


def user_post_blob_path(instance,filename):
    return f'upload/profile_pic/{instance.USER_POST_ID.USER_ID.username}/{filename}'
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
            self.password = make_password(self.password)
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