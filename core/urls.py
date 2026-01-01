from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication (login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),

    # Grievance app (main application)
    path('', include('grievance.urls')),
]

# Media files (development only)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
# =========================
# END OF FILE