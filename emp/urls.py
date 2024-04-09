from django.urls import path
from . import views

urlpatterns = [
    path('events/all/', views.view_all_events, name='view_all_events'),
    path('events/', views.view_event, name='view_event'),
    path('events/dept/', views.view_dept_events, name='view_dept_events'),
    path('events/create/', views.add_event, name='add_event'),
    path('events/edit/', views.edit_event, name='edit_event'),
    path('events/approve/', views.approve_event, name='approve_event'),
    path('events/reject/', views.disapprove_event, name='reject_event'),
    path('events/delete/', views.delete_event, name='delete_event'),
    path('events/members/add/', views.add_event_members, name='add_event_members'),
    path('rounds/add/', views.add_round, name='add_round'),
    path('rounds/edit/', views.edit_round, name='edit_round'),
    path('rounds/delete/', views.delete_round, name='delete_round'),
    path('forms/create/', views.create_event_form, name='create_event_form'),
    path('forms/edit/', views.edit_event_form, name='edit_event_form'),
    path('forms/', views.view_form, name='view_form'),
    path('reg_data/', views.view_event_reg_data, name='view_event_reg_data'),
    path('reg_data/csv/', views.get_csv_data, name='get_csv_data'),

]
