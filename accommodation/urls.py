from django.urls import path
from . import views


urlpatterns = [
    path('qr/<str:code>/', views.get_profile, name='get_profile'),
    path('student/<str:email>/', views.get_code_by_email, name='get_code_by_email'),
    path('student/id/<int:id>/',
         views.get_user_accommodation, name='get_user_accommodation'),
    path('student/<int:id>/checkin/', views.check_in, name='check_in'),
    path('student/<int:id>/checkout/', views.check_out, name='check_out'),
    path('student/<int:id>/checkin/status/',
         views.get_checkin_status, name='get_checkin_status'),
    path('student/<int:id>/supply/status',
         views.get_student_supplies, name='get_student_supplies'),
    path('student/<int:id>/cancheckout/',
         views.can_check_out, name='can_check_out'),
    path('otp/request/give/<int:id>/', views.request_supply_give_otp,
         name='request_supply_give_otp'),
    path('otp/request/return/<int:id>/', views.request_supply_return_otp,
         name='request_supply_return_otp'),
    path('otp/verify/give/<int:id>/', views.submit_supply_give_otp,
         name='submit_supply_give_otp'),
    path('otp/verify/return/<int:id>/', views.submit_supply_return_otp,
         name='submit_supply_return_otp'),
    path('supply/all', views.get_all_supplies, name='get_all_supplies'),
    path('volunteer/profile/', views.get_volunteer_info),
    path('hostel/all', views.get_all_hostels, name='get_all_hostels'),
    path('hostel/upcoming/<int:id>/',
         views.upcoming_students, name='upcoming_students')
]
