from django.urls import path
from . import views


urlpatterns = [
    path('volunteer/profile/', views.get_volunteer_info, name='get_volunteer_info'),
    path('events/', views.get_all_events, name='get_all_events'),
    path('events/<int:event_id>/', views.get_event_info, name='get_event_info'),
    path('student/<str:email>/', views.get_code_by_email, name='get_code_by_email'),
    path('student/event/checkin/<int:event_id>/<str:code>/',
         views.event_checkin, name='event_checkin'),
    path('student/fest/checkin/<str:code>/',
         views.fest_checkin, name='fest_checkin'),
    path('department/<int:id>/upload/',
         views.import_dept_members, name='import_dept_members'),
]
