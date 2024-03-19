from django.urls import path
from . import views

urlpatterns = [
    path('events/all/', views.view_all_events, name='view_all_events'),
    path('events/', views.view_event, name='view_event'),
    path('events/create/', views.add_event, name='add_event'),
    path('events/edit/', views.edit_event, name='edit_event'),
    path('events/delete/', views.delete_event, name='delete_event'),
    path('rounds/add/', views.add_round, name='add_round'),
    path('rounds/edit/', views.edit_round, name='edit_round'),
    path('rounds/delete/', views.delete_round, name='delete_round'),

]
