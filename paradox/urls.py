from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('frb/', include('frb.urls')),
    path('fest/', include('fest.urls')),
    path('base/', include('core.urls')),
    path('finance/', include('finance.urls')),
    path('emp/', include('emp.urls')),
    path('accommodation/', include('accommodation.urls')),
    path('sr/', include('sr.urls')),
    path('jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
