from django.urls import path
from . import views

urlpatterns = [
    path('bill/all/', views.get_all_bills, name='get_all_bills'),
    path('bill/id/<int:bill_id>/', views.get_bill, name='get_bill'),
    path('bill/user/', views.get_my_bills, name='get_my_bills'),
    path('bill/create/', views.upload_bill, name='upload_bill'),
    path('bill/first/approve/id/<int:bill_id>/',
         views.first_level_approval, name='first_level_approval'),
    path('bill/first/reject/id/<int:bill_id>/',
         views.first_level_rejection, name='first_level_rejection'),
    path('bill/final/approve/id/<int:bill_id>/',
         views.final_level_approval, name='final_level_approval'),
    path('bill/final/reject/id/<int:bill_id>/',
         views.final_level_rejection, name='final_level_rejection'),
    path('bill/approvedRequirements/', views.get_all_approved_requirements,
         name='get_all_approved_requirements'),
    path('bill/split/', views.create_split, name='create_split'),
    path('budget/balance/', views.get_balance, name='get_balance'),
    path('budget/allocate/department/<int:id>/',
         views.assign_dept_budget, name='assign_dept_budget'),
    path('budget/allocate/event/<int:event_id>/',
         views.assign_event_budget, name='assign_event_budget'),
    path('budget/deallocate/department/<int:id>/',
         views.deassign_dept_budget, name='deassign_dept_budget'),
    path('budget/deallocate/event/<int:event_id>/',
         views.deassign_event_budget, name='deassign_event_budget'),
    path('budget/department/all/', views.get_all_dept_accounts,
         name='get_all_dept_accounts'),
    path('transactions/', views.get_transactions, name='get_transactions'),
    path('transactions/<str:txn_type>/', views.get_txn_by_type,
         name='get_transactions_by_type'),
    path('dummy/', views.gen_dummy_vouch, name='gen_dummy_vouch'),
    path('voucher/all/', views.get_all_vouchers, name='get_all_vouchers'),
    path('voucher/csv/', views.voucher_csv, name='voucher_csv'),



]
