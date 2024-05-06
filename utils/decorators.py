from django.contrib.auth.models import Group, Permission
from django.db.models import QuerySet
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt import authentication
from functools import wraps
from core.models import Department, Event, SubDepartment
from frb.models import Requirement
from finance.models import Bill
from .fns import get_user_permissions


def authed():
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            auth = OAuth2Authentication()
            jwt_auth = authentication.JWTAuthentication()
            auth_tuple = auth.authenticate(
                request) or jwt_auth.authenticate(request)

            if not auth_tuple:
                return Response(
                    {'message': 'User is not authenticated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user = auth_tuple[0]
            print(f"user: {user}")
            if not user.is_authenticated:
                return Response(
                    {'message': 'User is not authenticated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            request.user = user
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def group_required(group_names):
    def decorator(view_func):
        @wraps(view_func)
        @authed()
        def wrapper(request, *args, **kwargs):
            for group_name in group_names:
                if request.user.groups.filter(name=group_name).exists():
                    return view_func(request, *args, **kwargs)
            return Response(
                {'message': 'User does not have permission'},
                status=status.HTTP_403_FORBIDDEN
            )
        return wrapper
    return decorator


def has_perms(perms: list):
    def decorator(view_func):
        @wraps(view_func)
        @authed()
        def wrapped_view(request, *args, **kwargs):
            # print(f"args: {args}")
            # print(f"kwargs: {kwargs}")

            user = request.user
            if not user.is_authenticated:
                return Response(
                    {'message': 'User is not authenticated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if request.method == 'GET':
                data = request.GET
                print(f"data: {data}")
            else:
                data = request.data

            department_id = data.get('dept_id')
            event_id = data.get('event_id')
            # event_id = kwargs.get('event_id')
            # department_id = kwargs.get('dept_id')
            # print(f"department_id: {department_id}")
            # print(f"event_id: {event_id}")
            if event_id:
                try:
                    event = Event.objects.get(id=event_id)
                    department = event.department
                except Event.DoesNotExist:
                    return Response(
                        {'message': 'Event does not exist'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            elif department_id:
                try:
                    department = Department.objects.get(id=department_id)
                    event = None
                except Department.DoesNotExist:
                    return Response(
                        {'message': 'Department does not exist'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                department = None
                event = None
            # print(f"department: {department}")
            secretary_group = Group.objects.get(name='secretary')
            user_permissions = get_user_permissions(user)
            found = 0
            groups = user.groups.all()
            all_group_permissions = [
                perm for group in groups for perm in user_permissions['groups'][group.name]]
            # print(f"all_group_permissions: {all_group_permissions}")
            permissions = Permission.objects.filter(
                codename__in=perms).all()
            # print(f"permissions: {permissions}")

            for perm in permissions:
                if perm in all_group_permissions:
                    found += 1
            if found != len(permissions):
                found = False
            else:
                found = True
            # print(f"found: {found}")
            if secretary_group not in user.groups.all() and not found:
                if event:
                    for perm in permissions:
                        if perm not in user_permissions['events'].get(event.id, []):
                            return Response(
                                {'message': 'User does not have permission'},
                                status=status.HTTP_403_FORBIDDEN
                            )

                elif department:
                    for perm in permissions:
                        # print(user_permissions['departments'][department.id])
                        if perm not in user_permissions['departments'].get(department.id, []):
                            return Response(
                                {'message': 'User does not have permission'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                else:
                    found = False
                    groups = user.groups.all()
                    for group in groups:
                        if user_permissions['groups'][group.name].intersection(permissions).count() == len(permissions):
                            found = True
                            break
                    if not found:
                        return Response(
                            {'message': 'User does not have permission'},
                            status=status.HTTP_403_FORBIDDEN
                        )

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def has_budget_perms(perms: list):
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
            dept_id = data.get('dept_id')
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
                if dept_id:
                    try:
                        department = Department.objects.get(id=dept_id)
                        # print(
                        #     f"user dept perms: {user_permissions['departments']}")
                        for perm in perm_objs:
                            dperms = user_permissions['departments'].get(
                                department.id, [])
                            if perm not in dperms:
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


def has_bill_perms(perms: list):
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
            bill_id = data.get('bill_id')
            dept_id = data.get('dept_id')
            event_id = data.get('event_id')
            sub_dept_id = data.get('sub_dept_id')
            perm_objs = Permission.objects.filter(codename__in=perms).all()
            user_permissions = get_user_permissions(user)
            # print(f"user_permissions: {user_permissions}")
            secretary_group = Group.objects.get(name='secretary')
            group_permissions = QuerySet[Permission]
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
                if bill_id:
                    try:
                        bill = Bill.objects.get(id=bill_id)
                        account = bill.account
                        dept = Department.objects.filter(
                            account=account).first()
                        event = Event.objects.filter(account=account).first()
                        sub_dept = SubDepartment.objects.filter(
                            account=account).first()
                        if event:
                            for perm in perm_objs:
                                if perm not in user_permissions['events'].get(event.id, []):
                                    return Response(
                                        {'message': 'User does not have permission'},
                                        status=status.HTTP_403_FORBIDDEN
                                    )
                        elif sub_dept:
                            for perm in perm_objs:
                                if perm not in user_permissions['sub_departments'].get(sub_dept.id, []):
                                    return Response(
                                        {'message': 'User does not have permission'},
                                        status=status.HTTP_403_FORBIDDEN
                                    )
                        elif dept:
                            for perm in perm_objs:
                                if perm not in user_permissions['departments'].get(dept.id, []):
                                    return Response(
                                        {'message': 'User does not have permission'},
                                        status=status.HTTP_403_FORBIDDEN
                                    )
                    except Bill.DoesNotExist:
                        return Response(
                            {'message': 'Bill does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif event_id:
                    try:
                        event = Event.objects.get(id=event_id)
                        department = event.department
                        for perm in perm_objs:
                            if perm not in user_permissions['events'].get(event.id, []):
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except Event.DoesNotExist:
                        return Response(
                            {'message': 'Event does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif dept_id:
                    try:
                        department = Department.objects.get(id=dept_id)
                        # print(
                        #     f"user dept perms: {user_permissions['departments']}")
                        for perm in perm_objs:
                            dperms = user_permissions['departments'].get(
                                department.id, [])
                            if perm not in dperms:
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except Department.DoesNotExist:
                        return Response(
                            {'message': 'Department does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif sub_dept_id:
                    try:
                        sub_department = SubDepartment.objects.get(
                            id=sub_dept_id)
                        for perm in perm_objs:
                            if perm not in user_permissions['sub_departments'].get(sub_department.id, []):
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except SubDepartment.DoesNotExist:
                        return Response(
                            {'message': 'Sub Department does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif not found:
                    return Response(
                        {'message': 'User does not have permission'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def has_requirement_perms(perms: list):
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
            req_id = data.get('req_id')
            dept_id = data.get('dept_id')
            event_id = data.get('event_id')
            sub_dept_id = data.get('sub_dept_id')
            perm_objs = Permission.objects.filter(codename__in=perms).all()
            user_permissions = get_user_permissions(user)
            secretary_group = Group.objects.get(name='secretary')
            group_permissions = QuerySet[Permission]
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
                if req_id:
                    try:
                        requirement = Requirement.objects.get(id=req_id)
                        event = requirement.event
                        department = event.department
                        sub_department = requirement.sub_department
                        if event:
                            for perm in perm_objs:
                                if perm not in user_permissions['events'].get(event.id, []):
                                    return Response(
                                        {'message': 'User does not have permission'},
                                        status=status.HTTP_403_FORBIDDEN
                                    )
                        elif sub_department:
                            for perm in perm_objs:
                                if perm not in user_permissions['sub_departments'].get(sub_department.id, []):
                                    return Response(
                                        {'message': 'User does not have permission'},
                                        status=status.HTTP_403_FORBIDDEN
                                    )
                        elif department:
                            for perm in perm_objs:
                                if perm not in user_permissions['departments'].get(department.id, []):
                                    return Response(
                                        {'message': 'User does not have permission'},
                                        status=status.HTTP_403_FORBIDDEN
                                    )
                    except Requirement.DoesNotExist:
                        return Response(
                            {'message': 'Requirement does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif event_id:
                    try:
                        event = Event.objects.get(id=event_id)
                        department = event.department
                        for perm in perm_objs:
                            if perm not in user_permissions['events'].get(event.id, []):
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except Event.DoesNotExist:
                        return Response(
                            {'message': 'Event does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif dept_id:
                    try:
                        department = Department.objects.get(id=dept_id)
                        # print(
                        #     f"user dept perms: {user_permissions['departments']}")
                        for perm in perm_objs:
                            dperms = user_permissions['departments'].get(
                                department.id, [])
                            if perm not in dperms:
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except Department.DoesNotExist:
                        return Response(
                            {'message': 'Department does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif sub_dept_id:
                    try:
                        sub_department = SubDepartment.objects.get(
                            id=sub_dept_id)
                        for perm in perm_objs:
                            if perm not in user_permissions['sub_departments'].get(sub_department.id, []):
                                return Response(
                                    {'message': 'User does not have permission'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                    except SubDepartment.DoesNotExist:
                        return Response(
                            {'message': 'Sub Department does not exist'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif not found:
                    return Response(
                        {'message': 'User does not have permission'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
