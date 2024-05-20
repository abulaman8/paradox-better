from django.contrib.auth.models import Group, Permission
from django.db.models import Q, QuerySet
from django.contrib.contenttypes.models import ContentType
from django.template import Context, Template
from django.core.files.base import ContentFile
from core.models import Department, Role, Event, SubDepartment
from finance.models import Bill, Voucher, VoucherType
from .templates import voucher_template, stact, sign, paradox_new_logo, empty
import pdfkit
import uuid


def get_user_permissions(user) -> dict[str, dict[str, QuerySet[Permission]]]:
    dept_type = ContentType.objects.get_for_model(Department)
    sub_dept_type = ContentType.objects.get_for_model(SubDepartment)
    event_type = ContentType.objects.get_for_model(Event)

    departments = Department.objects.filter(
        Q(core=user) | Q(members=user)).distinct()
    sub_departments = SubDepartment.objects.filter(
        Q(team_lead=user) | Q(members=user)).distinct()
    events = Event.objects.filter(
        Q(head=user) | Q(members=user)).distinct()
    department_permissions = {}
    sub_department_permissions = {}
    event_permissions = {}
    group_permissions = {}
    self_permissions = user.user_permissions.all()
    for dept in departments:
        department_permissions[dept.id] = dept.permissions.all()
        roles = Role.objects.filter(
            users=user,
            content_type=dept_type,
            object_id=dept.id
        ).all()
        for role in roles:
            department_permissions[dept.id] |= role.permissions.all()
    for sub_dept in sub_departments:
        sub_department_permissions[sub_dept.id] = sub_dept.permissions.all()
        roles = Role.objects.filter(
            users=user,
            content_type=sub_dept_type,
            object_id=sub_dept.id
        ).all()
        for role in roles:
            sub_department_permissions[sub_dept.id] |= role.permissions.all()

    for event in events:
        event_permissions[event.id] = event.permissions.all()
        roles = Role.objects.filter(
            users=user,
            content_type=event_type,
            object_id=event.id
        ).all()
        for role in roles:
            event_permissions[event.id] |= role.permissions.all()
    user_permissions = {}
    groups = user.groups.all()
    for group in groups:
        group_permissions[group.name] = group.permissions.all()
    user_permissions['departments'] = department_permissions
    user_permissions['sub_departments'] = sub_department_permissions
    user_permissions['events'] = event_permissions
    user_permissions['groups'] = group_permissions
    user_permissions['self'] = self_permissions

    return user_permissions


def generate_voucher(bill_id):
    bill = Bill.objects.prefetch_related(
        'vendor',
        'vendor__bank_details',
    ).get(id=bill_id)
    bill_type = bill.bill_type
    account = bill.account
    dc = Department.objects.filter(account=account).first()
    ec = Event.objects.filter(account=account).first()
    if dc:
        dept = dc
    elif ec:
        dept = ec.department
    else:
        dept = None
    voucher_type = VoucherType.objects.get(name=bill_type)
    img_data = "data:image/png;base64,"

    template = Template(voucher_template)
    data = {
        'voucher_number': f'VN-{bill_id}',
        'bill_number': bill.bill_number,
        'date': bill.bill_date.strftime('%d-%m-%Y'),
        'vendor': bill.vendor.name if bill.vendor else '',
        'dept': dept.name if dept else '',
        'vendor_address': bill.vendor.address if bill.vendor else '',
        'gst_number': bill.vendor.gst_number if bill.vendor else '',
        'type': voucher_type.name,
        'total': bill.amount,
        'description': bill.description,
        'stact': f'{img_data}{stact}',
        'sign': f'{img_data}{sign}',
        'logo': f'{img_data}{paradox_new_logo}',
        'account_number': bill.vendor.bank_details.account_number if bill.vendor and bill.vendor.bank_details else '',
        'ifsc': bill.vendor.bank_details.ifsc_code if bill.vendor and bill.vendor.bank_details else '',
        'account_holder': bill.vendor.bank_details.account_holder_name if bill.vendor and bill.vendor.bank_details else '',
        'bank': bill.vendor.bank_details.bank_name if bill.vendor and bill.vendor.bank_details else '',
        'empty': f'{img_data}{empty}',

    }
    # print(data)
    context = Context(data)

    voucher = template.render(context)
    pdf_file = pdfkit.from_string(voucher)
    voucher = Voucher.objects.create(
        bill=bill,
        voucher_type=voucher_type,
    )
    voucher.file.save(f'{uuid.uuid4()}.pdf',
                      ContentFile(pdf_file), save=True)  # type: ignore
    return True


def get_fin_permissions(obj, user_perms):
    view_vouchers = Permission.objects.filter(codename='view_voucher')
    view_bills = Permission.objects.filter(codename='view_bill')
    edit_bills = Permission.objects.filter(
        codename='change_bill')
    first_level_bill_approve = Permission.objects.filter(
        codename='first_level_bill_approval')
    first_level_bill_reject = Permission.objects.filter(
        codename='first_level_bill_rejection')
    final_level_bill_approve = Permission.objects.filter(
        codename='final_level_bill_approval')
    final_level_bill_reject = Permission.objects.filter(
        codename='final_level_bill_rejection')
    assign_dept_budget = Permission.objects.filter(
        codename='assign_dept_budget')
    deassign_dept_budget = Permission.objects.filter(
        codename='deassign_dept_budget')
    assign_event_budget = Permission.objects.filter(
        codename='assign_event_budget')
    deassign_event_budget = Permission.objects.filter(
        codename='deassign_event_budget')
    view_account = Permission.objects.filter(
        codename='view_account')
    create_split = Permission.objects.filter(
        codename='add_split')
    r = {}
    r['user_bills'] = {
        'view': True,
        'edit': True,
    }
    r['voucher'] = {
        'view': False,
    }
    r['department_bills'] = {}
    r['all_bills'] = {}
    r['all_budget'] = {}
    r['department_budget'] = {}
    r['department_account'] = {}
    r['all_account'] = {}
    r['all_bills']['view'] = False
    r['all_bills']['first_approve'] = False
    r['all_bills']['final_approve'] = False
    r['all_bills']['first_reject'] = False
    r['all_bills']['final_reject'] = False
    r['all_budget']['allocate'] = False
    r['all_budget']['deallocate'] = False
    r['all_account']['view'] = False
    r['department_bills']['view'] = False
    r['department_bills']['edit'] = False
    r['department_budget']['allocate'] = False
    r['department_budget']['deallocate'] = False
    r['department_account']['view'] = False
    r['split'] = False
    groups = user_perms['groups']
    departments = user_perms['departments']
    sub_departments = user_perms['sub_departments']
    events = user_perms['events']
    for group in groups:
        # print(groups[group])
        if create_split.first() in groups[group]:
            r['split'] = True
        if view_vouchers.first() in groups[group]:
            r['voucher']['view'] = True
        if view_bills.first() in groups[group]:
            r['all_bills']['view'] = True
        if first_level_bill_approve.first() in groups[group]:
            r['all_bills']['first_approve'] = True
        if final_level_bill_approve.first() in groups[group]:
            r['all_bills']['final_approve'] = True
        if first_level_bill_reject.first() in groups[group]:
            r['all_bills']['first_reject'] = True
        if final_level_bill_reject.first() in groups[group]:
            r['all_bills']['final_reject'] = True
        if assign_dept_budget.first() in groups[group]:
            r['all_budget']['allocate'] = True
        if deassign_dept_budget.first() in groups[group]:
            r['all_budget']['deallocate'] = True
        if view_account.first() in groups[group]:
            r['all_account']['view'] = True
    for dept in departments:
        if view_bills.first() in departments[dept]:
            r['department_bills']['view'] = True
        if edit_bills.first() in departments[dept]:
            r['department_bills']['edit'] = True
        if assign_event_budget.first() in departments[dept]:
            r['department_budget']['allocate'] = True
        if deassign_event_budget.first() in departments[dept]:
            r['department_budget']['deallocate'] = True
        if view_account.first() in departments[dept]:
            r['department_account']['view'] = True
    for sub_dept in sub_departments:
        if view_bills.first() in sub_departments[sub_dept]:
            r['department_bills']['view'] = True
        if edit_bills.first() in sub_departments[sub_dept]:
            r['department_bills']['edit'] = True
        if view_account.first() in sub_departments[sub_dept]:
            r['department_account']['view'] = True
    for event in events:
        if view_bills.first() in events[event]:
            r['department_bills']['view'] = True
        if edit_bills.first() in events[event]:
            r['department_bills']['edit'] = True
        if view_account.first() in events[event]:
            r['department_account']['view'] = True

    # get all group perms of user
    # user = obj

    return r


def get_emp_permissions(obj, user_perms):
    change_event = Permission.objects.filter(
        codename='change_event')
    add_event = Permission.objects.filter(codename='add_event')
    delete_event = Permission.objects.filter(codename='delete_event')
    approve_event = Permission.objects.filter(
        codename='approve_event')
    r = {}
    r['all'] = {
        'view': True,
        'edit': False,
        'delete': False,
        'approve': False,
        'add': False
    }
    r['department'] = {
        'view': True,
        'edit': False,
        'delete': False,
        'approve': False,
        'add': False
    }
    r['event'] = {
        'view': True,
        'edit': False,
        'delete': False,
        'approve': False,
        'add': False
    }

    groups = user_perms['groups']
    departments = user_perms['departments']
    events = user_perms['events']
    for group in groups:
        # print(groups[group])
        if change_event.first() in groups[group]:
            r['all']['edit'] = True
        if add_event.first() in groups[group]:
            r['all']['add'] = True
        if delete_event.first() in groups[group]:
            r['all']['delete'] = True
        if approve_event.first() in groups[group]:
            r['all']['approve'] = True
    for dept in departments:
        if change_event.first() in departments[dept]:
            r['department']['edit'] = True
        if add_event.first() in departments[dept]:
            r['department']['add'] = True
        if delete_event.first() in departments[dept]:
            r['department']['delete'] = True
        if approve_event.first() in departments[dept]:
            r['department']['approve'] = True
    for event in events:
        if change_event.first() in events[event]:
            r['event']['edit'] = True
        if add_event.first() in events[event]:
            r['event']['add'] = True
        if delete_event.first() in events[event]:
            r['event']['delete'] = True
        if approve_event.first() in events[event]:
            r['event']['approve'] = True

    # get all group perms of user
    # user = obj

    return r
