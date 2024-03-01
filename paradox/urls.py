from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('frb/', include('frb.urls')),
    path('fest/', include('fest.urls')),
    path('base/', include('core.urls')),
    path('finance/', include('finance.urls')),
]
