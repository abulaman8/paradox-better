from django.urls import path
from . import views

urlpatterns = [
    path('fest_register/', views.fest_registration, name='fest_registration'),
    path('accom_register/', views.accomodation_registration,
         name='accomodation_registration'),
    path('check_fest/', views.check_fest_registration,
         name='check_fest_registration'),
    path('check_accom/', views.check_accom, name='check_accom'),
    path('events/all/', views.get_events, name='get_events'),
    path('events/', views.get_event_by_id, name='get_event_by_id'),
    path('events/form/', views.get_event_form, name='get_event_form'),
    path('events/form/submit/', views.register_for_event,
         name='register_for_event'),
    path('events/form/edit/', views.edit_event_registration, name='edit_event'),
    path('events/registered/', views.get_registered_events,
         name='get_registered_events'),
    path('events/registered/<int:event_id>/',
         views.get_event_reg, name='get_event_reg'),
    path('events/registered/<int:event_id>/delete/',
         views.delete_reg, name='delete_reg'),
    path('user/exists/', views.check_user, name='check_user'),
    path('announcements/', views.get_all_announcements,
         name='get_all_announcements'),
    path('qr/', views.get_qr, name='get_qr'),
]
