from django.urls import path
from . import views


urlpatterns = [
    path('volunteer/profile/', views.get_volunteer_info, name='get_volunteer_info'),
    path('volunteed/all/', views.get_volunteer_info, name='get_volunteer_info'),
    path('volunteer/add/', views.add_volunteer, name='add_volunteer'),
    path('volunteer/edit/<int:id>/', views.update_volunteer, name='edit_volunteer'),
    path('volunteer/delete/<int:id>/',
         views.delete_volunteer, name='delete_volunteer'),
    path('events/', views.get_all_events, name='get_all_events'),
    path('events/<int:event_id>/', views.get_event_info, name='get_event_info'),
    path('student/<str:email>/', views.get_code_by_email, name='get_code_by_email'),
    path('student/event/checkin/<int:event_id>/<str:code>/',
         views.event_checkin, name='event_checkin'),
    path('student/fest/checkin/<str:code>/',
         views.fest_checkin, name='fest_checkin'),
    # path('department/<int:id>/upload/',
    #      views.import_dept_members, name='import_dept_members'),
    path('reset_shantanu/', views.reset_shantanu, name='reset_shantanu'),
    path('generate_qr/', views.generate_qr, name='generate_qr'),
]
