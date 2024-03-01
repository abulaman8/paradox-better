from django.urls import path
from . import views


urlpatterns = [
    path('requirements/download/', views.download_req_csv, name='download_req_csv'),
    path('resources/all/', views.get_all_resources, name='get_all_resources'),
    path('resources/measure_units/all/', views.get_all_units_of_measure,
         name='get_all_units_of_measure'),
    path('categories/all/', views.get_all_resource_categories,
         name='get_all_resource_categories'),
    path('requirements/request/',
         views.create_requirement, name='create_requirement'),
    path('requirements/all/', views.get_all_requirements,
         name='get_all_requirements'),
    path('requirements/category/<int:category_id>/',
         views.get_requirements_by_category, name='get_requirements_by_category'),
    path('requirements/user/', views.get_my_requirements,
         name='get_my_requirements'),
    path('requirements/id/<int:req_id>/',
         views.get_requirement, name='get_requirement'),
    path('requirements/status/<str:approval_status>/',
         views.get_requirement_by_status, name='get_requirements_by_status'),
    path('requirements/id/<int:req_id>/delete/',
         views.delete_requirement, name='delete_requirement'),
    path('requirements/id/<int:req_id>/edit/',
         views.update_my_requirement, name='update_requirement'),

    path('requirements/department/id/<int:req_id>/approve/',
         views.dept_core_approve_requirement, name='dept_approve_requirement'),
    path('requirements/department/id/<int:req_id>/reject/',
         views.dept_core_decline_requirement, name='dept_reject_requirement'),
    path('requirements/fr/first/<int:req_id>/approve/',
         views.fr_super_coord_approve_requirement, name='fr_super_coord_approve_requirement'),
    path('requirements/fr/first/<int:req_id>/reject/',
         views.fr_super_coord_decline_requirement, name='fr_super_coord_decline_requirement'),
    path('requirements/fr/last/<int:req_id>/approve/',
         views.fr_core_approve_requirement, name='fr_core_manage_requirement'),
    path('requirements/fr/last/<int:req_id>/reject/',
         views.fr_core_decline_requirement, name='fr_core_decline_requirement'),
    path('roles/members/add/', views.assign_fr_roles, name='assign_fr_roles'),
    path('roles/members/remove/', views.remove_fr_roles, name='remove_fr_roles'),
    path('roles/permissions/add/', views.add_fr_role_perms,
         name='set_fr_role_perms'),
    path('roles/permissions/remove/', views.remove_fr_role_perms,
         name='remove_fr_role_perms'),
    path('permissions/all/', views.get_fr_perms, name='get_fr_perms'),



]
