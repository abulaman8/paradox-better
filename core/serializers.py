from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.db.models import Q
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Department, Role, ApprovalStatus, SubDepartment, Event, Sponsor, FAQ, Link, Action
from utils.fns import get_emp_permissions, get_fin_permissions, get_user_permissions


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'content_type', 'codename']
        read_only_fields = ['id', 'name', 'content_type', 'codename']


class GroupSerializer(ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
        read_only_fields = ['id', 'name', 'permissions']


class ApprovalStatusSerializer(ModelSerializer):
    approval_status = SerializerMethodField()
    approved_by = SerializerMethodField()

    class Meta:
        model = ApprovalStatus
        fields = ['id', 'approval_status', 'approved_by']

    def get_approval_status(self, obj):
        return obj.name.split("_")[-1]

    def get_approved_by(self, obj):
        l = obj.name.split("_")[:-1]
        r = ""
        for i in l:
            r += i + " "
        return r.strip()


class ActionSerializer(ModelSerializer):
    user = SerializerMethodField()
    approval_status = ApprovalStatusSerializer()

    class Meta:
        model = Action
        fields = ['id', 'message', 'user', 'approval_status']
        read_only_fields = ['id', 'message', 'user', 'approval_status']

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class RoleSerializer(ModelSerializer):
    permissions = SerializerMethodField()
    department = SerializerMethodField()
    event = SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'department', 'event', 'permissions']
        read_only_fields = ['id', 'name', 'department', 'event', 'permissions']

    def get_permissions(self, obj):
        perms = obj.permissions.all()
        return [perms.codename for perms in perms]

    def get_department(self, obj):
        dep_type = ContentType.objects.get_for_model(Department)
        if obj.content_type == dep_type:
            return {
                "id": obj.object_id,
                "name": Department.objects.get(id=obj.object_id).name
            }
        return None

    def get_event(self, obj):
        event_type = ContentType.objects.get_for_model(Event)
        if obj.content_type == event_type:
            return {
                "id": obj.object_id,
                "name": Event.objects.get(id=obj.object_id).name
            }
        return None


class UserSerializer(ModelSerializer):
    groups = SerializerMethodField()
    permissions = SerializerMethodField()
    department = SerializerMethodField()
    sub_department = SerializerMethodField()
    event = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'groups', 'permissions', 'department', 'sub_department', 'event']

    def get_groups(self, obj):
        groups = obj.groups.all()
        return [group.name for group in groups]

    def get_department(self, obj):
        departments_qs: QuerySet[Department] = Department.objects.filter(
            Q(core=obj) | Q(members=obj)).distinct()
        print(f"departments_qs: {departments_qs}")
        if departments_qs.exists():
            dept = departments_qs.first()
            if dept:
                role = Role.objects.filter(
                    users=obj,
                    content_type=ContentType.objects.get_for_model(Department),
                    object_id=dept.id).first()
                return {
                    "id": dept.id,
                    "name": dept.name,
                    "role": role.name if role else "None"
                }
            else:
                return None
        return None

    def get_sub_department(self, obj):
        sub_departments_qs = SubDepartment.objects.filter(
            Q(team_lead=obj) | Q(members=obj)).distinct()
        if sub_departments_qs.exists():
            sub_dept = sub_departments_qs.first()
            if sub_dept:
                role = Role.objects.filter(
                    users=obj,
                    content_type=ContentType.objects.get_for_model(
                        SubDepartment),
                    object_id=sub_dept.id).first()
                return {
                    "id": sub_dept.id,
                    "name": sub_dept.name,
                    "role": role.name if role else "None"
                }
            else:
                return None

    def get_event(self, obj):
        events_qs = Event.objects.filter(
            Q(head=obj) | Q(members=obj)).distinct()
        if events_qs.exists():
            event = events_qs.first()
            if event:
                role = Role.objects.filter(
                    users=obj,
                    content_type=ContentType.objects.get_for_model(Event),
                    object_id=event.id).first()
                return {
                    "id": event.id,
                    "name": event.name,
                    "role": role.name if role else "None"
                }
            else:
                return None
        return None

    def get_permissions(self, obj):
        view_req = Permission.objects.filter(codename='view_requirement')
        edit_req = Permission.objects.filter(
            codename='change_requirement')
        first_level_req_approve = Permission.objects.filter(
            codename='first_level_req_approval')
        first_level_req_reject = Permission.objects.filter(
            codename='first_level_req_rejection')
        second_level_req_approve = Permission.objects.filter(
            codename='second_level_req_approval')
        final_level_req_approve = Permission.objects.filter(
            codename='final_level_req_approval')
        second_level_req_reject = Permission.objects.filter(
            codename='second_level_req_rejection')
        final_level_req_reject = Permission.objects.filter(
            codename='final_level_req_rejection')
        r = {}
        r['my_req'] = {}
        r['dept_req'] = {}
        r['all_req'] = {}
        r['all_req']['view'] = False
        r['all_req']['first approve'] = False
        r['all_req']['final approve'] = False
        r['all_req']['first reject'] = False
        r['all_req']['final reject'] = False
        r['dept_req']['view'] = False
        r['dept_req']['edit'] = False
        r['dept_req']['approve'] = False
        r['dept_req']['reject'] = False
        user_perms = get_user_permissions(obj)
        groups = user_perms['groups']
        departments = user_perms['departments']
        sub_departments = user_perms['sub_departments']
        events = user_perms['events']
        for group in groups:
            print(groups[group])
            if view_req.first() in groups[group]:
                r['all_req']['view'] = True
            if second_level_req_approve.first() in groups[group]:
                r['all_req']['first approve'] = True
            if final_level_req_approve.first() in groups[group]:
                r['all_req']['final approve'] = True
            if second_level_req_reject.first() in groups[group]:
                r['all_req']['first reject'] = True
            if final_level_req_reject.first() in groups[group]:
                r['all_req']['final reject'] = True
        for dept in departments:
            if view_req.first() in departments[dept]:
                r['dept_req']['view'] = True
            if edit_req.first() in departments[dept]:
                r['dept_req']['edit'] = True
            if first_level_req_approve.first() in departments[dept]:
                r['dept_req']['approve'] = True
            if first_level_req_reject.first() in departments[dept]:
                r['dept_req']['reject'] = True
        for sub_dept in sub_departments:
            if view_req.first() in sub_departments[sub_dept]:
                r['dept_req']['view'] = True
            if edit_req.first() in sub_departments[sub_dept]:
                r['dept_req']['edit'] = True
        for event in events:
            if view_req.first() in events[event]:
                r['dept_req']['view'] = True
            if edit_req.first() in events[event]:
                r['dept_req']['edit'] = True

        # get all group perms of user
        # user = obj

        r['my_req']['view'] = True
        r['my_req']['edit'] = True
        r['my_req']['delete'] = True
        final = {}
        final['frb'] = r
        final['finance'] = get_fin_permissions(obj, user_perms)
        final['emp'] = get_emp_permissions(obj, user_perms)
        return final


class SimpleUserSerializer(ModelSerializer):
    roles = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'roles']
        read_only_fields = ['id', 'username',
                            'email', 'first_name', 'last_name', 'roles']

    def get_roles(self, obj):
        roles = Role.objects.filter(users=obj).all()
        return [[str(role.content_object), role.name] for role in roles]


class DepartmentSerializer(ModelSerializer):
    core = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'core']
        read_only_fields = ['id', 'core', 'name']


class SubDepartmentSerializer(ModelSerializer):
    team_lead = SimpleUserSerializer(read_only=True)

    class Meta:
        model = SubDepartment
        fields = ['id', 'name', 'department', 'team_lead']
        read_only_fields = ['id', 'name', 'department', 'team_lead']


class EventSerializer(ModelSerializer):
    head = SimpleUserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Event
        exclude = ['account', 'members']


class DepartmentCreateSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']


class DepartmentDetailSerializer(ModelSerializer):
    core = SimpleUserSerializer(read_only=True)
    deputy_core = SimpleUserSerializer(read_only=True)
    members = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'core', 'deputy_core', 'members']
        read_only_fields = ['id', 'name', 'core', 'deputy_core', 'members']


class SponsorSerializer(ModelSerializer):
    class Meta:
        model = Sponsor
        exclude = ['content_type', 'object_id']


class FAQSerializer(ModelSerializer):
    class Meta:
        model = FAQ
        exclude = ['content_type', 'object_id']


class LinkSerializer(ModelSerializer):
    class Meta:
        model = Link
        exclude = ['content_type', 'object_id']
