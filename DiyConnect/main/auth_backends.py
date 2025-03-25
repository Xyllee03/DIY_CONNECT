from django.contrib.auth.backends import BaseBackend
from .models import UserSites  # Import your model
from django.contrib.auth.hashers import check_password

class UserSiteBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = UserSites.objects.get(username=username)
        except UserSites.DoesNotExist:
            return None

        if check_password(password, user.password):
            return user  # Return the user object

        return None

    def get_user(self, user_id):
        try:
            return UserSites.objects.get(pk=user_id)
        except UserSites.DoesNotExist:
            return None
