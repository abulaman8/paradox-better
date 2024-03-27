from django.contrib.auth.models import Group, Permission
from django.db.models import Q, QuerySet
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import authentication_classes
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from core.models import Department, Role, Event, SubDepartment
from frb.models import Requirement
from finance.models import Bill
from utils.decorators import authed
from utils.fns import get_user_permissions


def has_event_perms(perms: list):
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
            event_id = data.get('event_id')
            perm_objs = Permission.objects.filter(codename__in=perms).all()
            user_permissions = get_user_permissions(user)
            secretary_group = Group.objects.get(name='secretary')
            found = 0
            groups = user.groups.all()
            all_group_permissions = [
                perm for group in groups for perm in user_permissions['groups'][group.name]]
            # print(f"all_group_permissions: {all_group_permissions}")

            for perm in perm_objs:
                if perm in all_group_permissions:
                    found += 1
            if found != len(perm_objs):
                found = False
            else:
                found = True
            # print(f"found: {found}")

            if secretary_group not in user.groups.all() and not found:
                if event_id:
                    try:
                        event = Event.objects.get(id=event_id)
                        department = event.department
                        # print(
                        #     f"user dept perms: {user_permissions['departments']}")
                        for perm in perm_objs:
                            dperms = user_permissions['departments'].get(
                                department.id, [])
                            event_perms = user_permissions['events'].get(
                                event.id, [])
                            if perm not in dperms and perm not in event_perms:
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except Department.DoesNotExist:
                        return Response(
                            {'message': 'Department does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
