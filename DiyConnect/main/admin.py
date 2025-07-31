from django.contrib import admin
from .models import UserSites, UserPost, UserPost_BLOB, Friendships, UserMessages,TaskRequest, Review
# Register your models here.
admin.site.register(UserSites)
admin.site.register(UserPost)
admin.site.register(UserPost_BLOB)
admin.site.register(Friendships)
admin.site.register(UserMessages)
admin.site.register(TaskRequest)
admin.site.register(Review)
