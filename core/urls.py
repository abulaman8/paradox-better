from django.urls import path
from . import views

urlpatterns = [
    path('approval_status/all/', views.get_all_approval_statuses,
         name='get_all_approval_statuses'),
    path('profile/', views.get_profile, name='get_profile'),
    path('department/create/', views.create_dept, name='create_dept'),
    path('department/all/', views.get_all_depts, name='get_all_depts'),
    path('department/', views.get_dept, name='get_dept'),
    path('department/edit/', views.edit_dept, name='edit_dept'),
    path('department/delete', views.delete_dept, name='delete_dept'),
    path('department/assign/core/',
         views.set_dept_core, name='set_core'),
    path('department/assign/members/',
         views.add_members, name='add_members'),
    path('department/remove/members/',
         views.delete_members, name='delete_members'),
    path('roles/all/', views.get_all_groups, name='get_all_groups'),
    path('roles/create/', views.create_group, name='create_group'),
    path('roles/department/assign/members/',
         views.assign_dept_user_roles, name='assign_roles'),
    path('permissions/all/', views.get_dept_perms, name='get_all_perms'),

    path('permissions/department/<int:id>/role/set/',
         views.set_dept_role_perms, name='set_dept_roles_perms'),
    path('roles/user/', views.get_my_roles, name='get_my_roles'),
    path('roles/<str:role_name>/', views.get_role_members, name='get_role_members'),
    path('roles/department/<int:id>/',
         views.get_my_roles_in_dept, name='get_my_roles_by_dept'),
    path('blacklist/add/', views.add_blacklist, name='add_blacklist'),
    path('blacklist/all/', views.get_blacklist, name='get_blacklist'),
    path('blacklist/<int:id>/delete/',
         views.remove_blacklist, name='delete_blacklist'),


]
