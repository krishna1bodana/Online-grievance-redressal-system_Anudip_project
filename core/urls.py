from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication (Standard Django login/logout/password management)
    path('accounts/', include('django.contrib.auth.urls')),

    # Grievance app (Main application logic)
    path('', include('grievance.urls', namespace='grievance')),
]

# Serving Media and Static files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
    )