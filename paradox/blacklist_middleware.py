from django.http import HttpResponseForbidden
from core.models import Blacklist
from oauth2_provider.contrib.rest_framework import OAuth2Authentication


class BlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.oauth2_authentication = OAuth2Authentication()

    def __call__(self, request):
        auth_tuple = self.oauth2_authentication.authenticate(request)
        if auth_tuple is not None:
            request.user = auth_tuple[0]
        if request.user.is_authenticated:
            user_email = request.user.email
            if Blacklist.objects.filter(email=user_email).exists():
                print(
                    f"User {user_email} is blacklisted from accessing this resource.")
                return HttpResponseForbidden("You are blacklisted from accessing this resource.")
        else:
            print("User is not authenticated.")

        response = self.get_response(request)
        return response
