# grievance/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class RequireEmailMiddleware:
    """
    Forces authenticated users to complete their profile
    (email required) before accessing the application.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Resolve allowed URLs once (performance + safety)
        self.complete_profile_url = reverse('grievance:complete_profile')
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')

    def __call__(self, request):
        # Skip unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        # Skip admin, static, media
        if (
            path.startswith('/admin/')
            or path.startswith(settings.STATIC_URL)
            or path.startswith(settings.MEDIA_URL)
        ):
            return self.get_response(request)

        # Allow auth-related pages
        if path in {
            self.complete_profile_url,
            self.logout_url,
            self.login_url,
        }:
            return self.get_response(request)

        # Enforce email completion
        if not request.user.email:
            return redirect(self.complete_profile_url)

        return self.get_response(request)
# End of middleware.py