from django.urls import path
from . import views

urlpatterns = [
    path('fest_register/', views.fest_registration, name='fest_registration'),
    path('accom_register/', views.accomodation_registration,
         name='accomodation_registration'),
    path('check_fest/', views.check_fest_registration,
         name='check_fest_registration'),
]
