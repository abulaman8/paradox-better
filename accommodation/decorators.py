from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from core.models import Department
from utils.decorators import authed
from utils.fns import get_user_permissions


def has_accom_perms(perms: list):
    def decorator(view_func):
        @wraps(view_func)
        @authed()
        def wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {'message': 'User is not authenticated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if request.method == 'GET':
                data = request.GET
                # print(f"data: {data}")
            else:
                data = request.data
                # print(f"data: {data}")
            perm_objs = Permission.objects.filter(codename__in=perms).all()
            user_permissions = get_user_permissions(user)
            secretary_group = Group.objects.get(name='secretary')
            found = 0
            groups = user.groups.all()
            all_group_permissions = [
                perm for group in groups for perm in user_permissions['groups'][group.name]]
            for perm in perm_objs:
                if perm in all_group_permissions:
                    found += 1
            dept = Department.objects.get(name="Accommodation")
            for perm in perm_objs:
                if perm in user_permissions['departments'].get(dept.id, []):
                    found += 1

            if found < len(perm_objs):
                found = False
            else:
                found = True
            # print(f"found: {found}")

            if secretary_group not in user.groups.all() and not found:
                return Response(
                    {'message': 'User does not have permission'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
