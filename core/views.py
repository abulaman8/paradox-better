from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomRole, Department, Role, ApprovalStatus, Blacklist
from core.serializers import DepartmentDetailSerializer, DepartmentSerializer, PermissionSerializer, RoleSerializer, UserSerializer, ApprovalStatusSerializer
from utils.decorators import authed, has_perms, group_required


@api_view(['GET'])
def get_all_approval_statuses(request):
    approval_statuses = ApprovalStatus.objects.all()
    serialized = ApprovalStatusSerializer(approval_statuses, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@group_required('secretary')
def create_group(request):
    data = request.data
    name = data.get('name')
    try:
        group, created = CustomRole.objects.get_or_create(name=name)
        if not created:
            return Response({'message': 'Group already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Group created'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@group_required(['secretary'])
def add_blacklist(request):
    data = request.data
    email = data.get('email')
    Blacklist.objects.create(email=email)
    return Response({'message': 'Blacklisted'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@group_required(['secretary'])
def get_blacklist(request):
    blacklist = Blacklist.objects.all()
    serialized = [{'id': b.id, 'email': b.email} for b in blacklist]
    return Response(serialized, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@group_required(['secretary'])
def remove_blacklist(request, id):
    try:
        blacklist = Blacklist.objects.get(id=id)
        blacklist.delete()
    except Blacklist.DoesNotExist:
        return Response({'error': 'Blacklist not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'message': 'Blacklist removed'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_groups(request):
    groups = Group.objects.all()
    names = [group.name for group in groups]
    return Response(names, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_custom_roles(request):
    custom_roles = CustomRole.objects.all()
    data = [cr.name for cr in custom_roles]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_perms(['view_role'])
def get_role_members(request, role_name):
    depts = Department.objects.all()
    r = []
    for dept in depts:
        d = {}
        d['department'] = dept.name
        d['members'] = []
        role = Role.objects.filter(
            name=role_name,
            content_type=ContentType.objects.get_for_model(Department),
            object_id=dept.id
        ).first()
        if role:
            d['members'] = [
                f"{user.first_name} {user.last_name}" for user in role.users.all()]
        else:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
        r.append(d)

    return Response(r, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_perms(['view_department'])
def get_all_depts(request):
    depts = Department.objects.all()
    serialized = DepartmentSerializer(depts, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_perms(['view_department'])
def get_dept(request):
    data = request.GET
    id = data.get('dept_id')
    try:
        dept = Department.objects.get(id=id)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    serialized = DepartmentDetailSerializer(dept)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_perms(['view_department'])
def get_dept_perms(request):
    try:
        req_type = ContentType.objects.get(
            app_label='frb',
            model='requirement'
        )
        role_type = ContentType.objects.get(
            app_label='core',
            model='role'
        )
        dept_type = ContentType.objects.get_for_model(Department)
        bill_type = ContentType.objects.get(
            app_label='finance',
            model='bill'
        )
        permissions = Permission.objects.filter(
            content_type_in=[req_type, role_type, dept_type, bill_type]).all()
        r = [perm.codename for perm in permissions]
        return Response(r, status=status.HTTP_200_OK)

    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_perms(['change_department'])
def set_dept_core(request, id):
    data = request.data
    email = data.get('email')
    print(email)
    try:
        user = User.objects.get(email=email)
        dept = Department.objects.get(id=id)
        try:
            core = dept.core
        except Exception as e:
            core = None
        print(core)
        if core:
            Role.objects.filter(department=dept, user=core).update(user=user)
        else:
            req_type = ContentType.objects.get(
                app_label='frb',
                model='requirement'
            )
            role_type = ContentType.objects.get(
                app_label='core',
                model='role'
            )
            permissions = Permission.objects.filter(
                content_type=req_type).all()
            role_permissions = Permission.objects.filter(
                content_type=role_type).all()

            core_roles = Role.objects.create(
                user=user,
                name="core",
                department=dept,
            )
            core_roles.permissions.set(permissions)
            core_roles.permissions.add(*role_permissions)

        dept.core = user
        dept.save()
        return Response({'message': 'Core set'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_all_permissions(request):
    dept_type = ContentType.objects.get_for_model(Department)
    roles_type = ContentType.objects.get_for_model(Role)
    req_type = ContentType.objects.get(
        app_label='frb',
        model='requirement'
    )
    permissions = Permission.objects.filter(content_type=dept_type).all()
    permissions = permissions.union(
        Permission.objects.filter(content_type=roles_type).all())
    permissions = permissions.union(
        Permission.objects.filter(content_type=req_type).all())
    codenames = [perm.codename for perm in permissions]
    # serialized = PermissionSerializer(permissions, many=True)
    return Response(codenames, status=status.HTTP_200_OK)


@api_view(['GET'])
# @authed()
@authed()
def get_profile(request):
    user = request.user
    serialized = UserSerializer(user)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authed()
def get_my_roles(request):
    user = request.user
    roles = Role.objects.filter(users=user).all()
    serialized = RoleSerializer(roles, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authed()
def get_my_roles_in_dept(request, id):
    user = request.user
    try:
        dept = Department.objects.get(id=id)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    roles = Role.objects.filter(user=user, department=dept).all()
    serialized = RoleSerializer(roles, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_perms(['add_department'])
def create_dept(request):
    data = request.data
    name = data.get('name')
    core = data.get('core')
    event_based = data.get('event_based')
    try:
        core_object = User.objects.get(email=core)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        try:

            dept = Department.objects.create(
                name=name, core=core_object, event_based=True if event_based else False)
            dept.save()
            dept_default_perm_codes = [
                "view_requirement", "add_requirement", "view_bill", "add_bill", "view_department"]
            dept_default_perms = Permission.objects.filter(
                codename__in=dept_default_perm_codes).all()
            dept.permissions.set(dept_default_perms)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    serialized = DepartmentSerializer(dept)
    return Response(serialized.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@group_required('secretary')
def edit_dept(request):
    data = request.data
    id = data.get('id')
    name = data.get('name')
    core = data.get('core')
    members = data.get('members')

    try:
        with transaction.atomic():
            dept = Department.objects.get(id=id)
            core_group = Group.objects.get(name='core')
            dept.core.groups.remove(core_group)
            core_object = User.objects.get(email=core)
            core_object.groups.add(core_group)
            dept.core = core_object
            members_objects = User.objects.filter(email__in=members).all()
            dept.members.set(members_objects)
            dept.name = name
            dept.save()
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    serialized = DepartmentSerializer(dept)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@has_perms(['change_department'])
def delete_members(request):
    data = request.data
    id = data.get('dept_id')
    members = data.get('members')
    member_objects = []
    for member in members:
        try:
            member_objects.append(User.objects.get(email=member))
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        dept = Department.objects.get(id=id)
        dept.members.remove(*member_objects)
        Role.objects.filter(department=dept, user__in=member_objects).delete()
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@has_perms(['change_department'])
def add_members(request):
    data = request.data
    id = data.get('dept_id')
    print(id)
    members = data.get('members')
    member_objects = []
    for member in members:
        try:
            member_objects.append(User.objects.get(email=member))
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        dept = Department.objects.get(id=id)
        dept.members.add(*member_objects)
        return Response({'message': 'Members added'}, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return Response({'error': 'Department does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@group_required('secretary')
def delete_dept(request):
    data = request.data
    id = data.get('dept_id')
    try:
        dept = Department.objects.get(id=id)
        dept.delete()
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'message': 'Department deleted'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_perms(['add_role'])
def assign_dept_user_roles(request):
    data = request.data
    id = data.get('dept_id')
    name = data.get('name')
    members = data.get('members')
    try:
        dept = Department.objects.get(id=id)
        cr = CustomRole.objects.get(name=name)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    except CustomRole.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

    role, _ = Role.objects.get_or_create(
        name=name, content_type=ContentType.objects.get_for_model(Department), object_id=dept.id)

    member_objects = []
    for member in members:
        try:
            member_objects.append(User.objects.get(email=member))
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    role.users.add(*member_objects)
    return Response({'message': 'Roles created'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@has_perms(['change_role'])
def set_dept_role_perms(request, id):
    data = request.data
    name = data.get('name')
    perms = data.get('perms')
    try:
        dept = Department.objects.get(id=id)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    perms_objects = []
    for perm in perms:
        try:
            perms_objects.append(Permission.objects.get(codename=perm))
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    role = Role.objects.filter(name=name, department=dept)
    if not role.exists():
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    role = role.first()
    if not role:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    role.permissions.set(perms_objects)
    return Response({'message': 'Permissions set'}, status=status.HTTP_200_OK)
