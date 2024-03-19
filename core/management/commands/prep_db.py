from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from core.models import ApprovalStatus, Department, Event
from frb.models import ResourceCategory, Requirement
from finance.models import Bill


class Command(BaseCommand):

    help = 'Prepares the database by creating the necessary groups and approval status.'

    def handle(self, *args, **options):
        Group.objects.get_or_create(name='secretary')
        Group.objects.get_or_create(name='fr_core')
        Group.objects.get_or_create(name='fr_super_coordinator')
        Group.objects.get_or_create(name='fr_coordinator')
        Group.objects.get_or_create(name='fr_volunteer')
        Group.objects.get_or_create(name='fin_core')
        Group.objects.get_or_create(name='fin_super_coordinator')
        Group.objects.get_or_create(name='fin_coordinator')
        Group.objects.get_or_create(name='fin_volunteer')
        ApprovalStatus.objects.get_or_create(name='pending')
        ResourceCategory.objects.get_or_create(name='other')
        ApprovalStatus.objects.get_or_create(name='first_level_approved')
        ApprovalStatus.objects.get_or_create(name='second_level_approved')
        ApprovalStatus.objects.get_or_create(name='final_level_approved')
        ApprovalStatus.objects.get_or_create(name='first_level_rejected')
        ApprovalStatus.objects.get_or_create(name='second_level_rejected')
        ApprovalStatus.objects.get_or_create(name='final_level_rejected')
        req_type = ContentType.objects.get_for_model(Requirement)
        department_type = ContentType.objects.get_for_model(Department)
        event_type = ContentType.objects.get_for_model(Event)
        bill_type = ContentType.objects.get_for_model(Bill)
        Permission.objects.get_or_create(
            codename='first_level_req_approval',
            name='Can approve requirements at first level',
            content_type=req_type
        )
        Permission.objects.get_or_create(
            codename='second_level_req_approval',
            name='Can approve requirements at second level',
            content_type=req_type
        )
        Permission.objects.get_or_create(
            codename='final_level_req_approval',
            name='Can approve requirements at final level',
            content_type=req_type
        )
        Permission.objects.get_or_create(
            codename='first_level_req_rejection',
            name='Can reject requirements at first level',
            content_type=req_type
        )
        Permission.objects.get_or_create(
            codename='second_level_req_rejection',
            name='Can reject requirements at second level',
            content_type=req_type
        )
        Permission.objects.get_or_create(
            codename='final_level_req_rejection',
            name='Can reject requirements at final level',
            content_type=req_type
        )
        Permission.objects.get_or_create(
            codename='first_level_bill_approval',
            name='Can approve bills at first level',
            content_type=bill_type
        )
        Permission.objects.get_or_create(
            codename='final_level_bill_approval',
            name='Can approve bills at final level',
            content_type=bill_type
        )
        Permission.objects.get_or_create(
            codename='first_level_bill_rejection',
            name='Can reject bills at first level',
            content_type=bill_type
        )
        Permission.objects.get_or_create(
            codename='final_level_bill_rejection',
            name='Can reject bills at final level',
            content_type=bill_type
        )
        Permission.objects.get_or_create(
            codename='assign_dept_budget',
            name='Can assign budget to departments',
            content_type=department_type
        )
        Permission.objects.get_or_create(
            codename='deassign_dept_budget',
            name='Can deassign budget to departments',
            content_type=department_type
        )
        Permission.objects.get_or_create(
            codename='assign_event_budget',
            name='Can assign budget to events',
            content_type=event_type
        )
        Permission.objects.get_or_create(
            codename='deassign_event_budget',
            name='Can deassign budget to events',
            content_type=event_type
        )
        Permission.objects.get_or_create(
            codename='approve_event',
            name='Can approve events',
            content_type=event_type
        )

        Permission.objects.get_or_create(
            codename='manage_member',
            name='Can manage members of the department',
            content_type=department_type
        )

        self.stdout.write(self.style.SUCCESS('Database has been prepared.'))
