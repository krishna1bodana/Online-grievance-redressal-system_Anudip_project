# middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RequireEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.email:
                allowed = [
                    reverse('grievance:complete_profile'),
                    reverse('logout'),
                ]
                if request.path not in allowed:
                    return redirect('grievance:complete_profile')

        return self.get_response(request)
# End of middleware.py