from django.contrib.auth.models import Permission, Group, User
from django.http import HttpResponse
from django.shortcuts import render
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from utils.decorators import has_requirement_perms
from core.models import ApprovalStatus, Department, Event, Role
from .models import Requirement, Resource, ResourceCategory, UnitOfMeasure
from .serializers import RequirementSerializer, ResourceCategorySerializer, UnitOfMeasureSerializer, ResourceSerializer
import csv


@api_view(['GET'])
def get_all_units_of_measure(request):
    units_of_measure = UnitOfMeasure.objects.all()
    serialized = UnitOfMeasureSerializer(units_of_measure, many=True)
    return Response(
        serialized.data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def get_all_resources(request):
    resources = Resource.objects.all()
    serialized = ResourceSerializer(resources, many=True)
    return Response(

        serialized.data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def get_all_resource_categories(request):
    resource_categories = ResourceCategory.objects.all()
    serialized = ResourceCategorySerializer(resource_categories, many=True)
    return Response(
        serialized.data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@has_requirement_perms(['view_requirement'])
def get_requirements_by_category(request, category_id):
    data = request.GET
    id = int(data.get('dept_id', 0))
    event_id = int(data.get('event_id', 0))
    try:
        category = ResourceCategory.objects.get(id=category_id)
        resources = Resource.objects.filter(category=category).all()
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                requirements = Requirement.objects.filter(
                    resource__in=resources, event=event).all()
                serialized = RequirementSerializer(requirements, many=True)
                return Response(
                    serialized.data,
                    status=status.HTTP_200_OK
                )
            except Event.DoesNotExist:
                return Response(
                    {"message": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif id:
            try:
                department = Department.objects.get(id=id)
                events = Event.objects.filter(department=department).all()
                dept_requirements = Requirement.objects.filter(
                    resource__in=resources, department=department).all()
                event_requirements = Requirement.objects.filter(
                    resource__in=resources, event__in=events).all()
                requirements = dept_requirements.union(event_requirements)
                serialized = RequirementSerializer(requirements, many=True)
                return Response(
                    serialized.data,
                    status=status.HTTP_200_OK
                )
            except Department.DoesNotExist:
                return Response(
                    {"message": "Department not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        requirements = Requirement.objects.filter(resource__in=resources).all()
        serialized = RequirementSerializer(requirements, many=True)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except ResourceCategory.DoesNotExist:
        return Response(
            {"message": "Category not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@has_requirement_perms(['add_requirement'])
def create_requirement(request):
    data = request.data
    event_id = int(data.get("event_id", 0))
    id = int(data.get("dept_id", 0))
    resource = data.get("resource")
    quantity = data.get("quantity")
    description = data.get("description")
    unit_of_measure = data.get("unit_of_measure")
    category = data.get("category")
    author = request.user
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            department = event.department
        except Event.DoesNotExist:
            return Response(
                {"message": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    else:

        try:
            department = Department.objects.get(id=id)
            event = None

        except Department.DoesNotExist:
            return Response(
                {"message": "Department not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    category_object, _ = ResourceCategory.objects.get_or_create(
        name=category.lower())
    unit_of_measure_object, _ = UnitOfMeasure.objects.get_or_create(
        name=unit_of_measure.lower())
    pending = ApprovalStatus.objects.get(name="pending")
    resource_object, created = Resource.objects.get_or_create(
        name=resource.lower(), unit_of_measure=unit_of_measure_object)
    if created:
        resource_object.category = category_object
        resource_object.save()
    requirement = Requirement.objects.create(
        resource=resource_object,
        quantity=quantity,
        description=description,
        author=author,
        approval_status=pending,
        department=department,
        event=event
    )
    serializer = RequirementSerializer(requirement)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@has_requirement_perms(['view_requirement'])
def get_all_requirements(request):
    data = request.GET
    event_id = int(data.get("event_id", 0))
    id = int(data.get("dept_id", 0))
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            requirements = Requirement.objects.filter(event=event).all()
            serialized = RequirementSerializer(requirements, many=True)
            return Response(
                serialized.data,
                status=status.HTTP_200_OK
            )

        except Event.DoesNotExist:
            return Response({"message": "Event not found"})
    elif id:
        try:
            department = Department.objects.get(id=id)
            events = Event.objects.filter(department=department).all()
            dept_requirements = Requirement.objects.filter(
                department=department).all()
            event_requirements = Requirement.objects.filter(
                event__in=events).all()
            requirements = dept_requirements.union(event_requirements)
            serialized = RequirementSerializer(requirements, many=True)
            return Response(
                serialized.data,
                status=status.HTTP_200_OK
            )
        except Department.DoesNotExist:
            return Response(
                {"message": "Department not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    requirements = Requirement.objects.all()
    serialized = RequirementSerializer(requirements, many=True)
    return Response(
        serialized.data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
def get_my_requirements(request):
    requirements = Requirement.objects.filter(author=request.user)
    serialized = RequirementSerializer(requirements, many=True)
    return Response(
        serialized.data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
# @has_perms(['view_requirement'])
@has_requirement_perms(['view_requirement'])
def get_requirement(request, req_id):
    data = request.GET
    event_id = int(data.get("event_id", 0))
    id = int(data.get("dept_id", 0))
    try:
        requirement = Requirement.objects.get(id=req_id)
        dept = requirement.department
        event = requirement.event
        if (event and event_id and event.id != event_id) or (dept and id and dept.id != id):
            if event:
                print(event.id, event_id)
            if dept:
                print(dept.id, id)
                print(type(dept.id), type(id))
                print(dept.id != id)

            return Response(
                {"message": "Requirement not found, wink wink"},
                status=status.HTTP_404_NOT_FOUND
            )
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )

    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@has_requirement_perms(['view_requirement'])
def get_requirement_by_status(request, approval_status):
    data = request.GET
    event_id = int(data.get("event_id", 0))
    id = int(data.get("dept_id", 0))
    try:
        approval_status = ApprovalStatus.objects.get(
            name=approval_status.lower())
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                requirements = Requirement.objects.filter(
                    approval_status=approval_status, event=event).all()
                serialized = RequirementSerializer(requirements, many=True)
                return Response(
                    serialized.data,
                    status=status.HTTP_200_OK
                )
            except Event.DoesNotExist:
                return Response(
                    {"message": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif id:
            try:
                department = Department.objects.get(id=id)
                events = Event.objects.filter(department=department).all()
                dept_requirements = Requirement.objects.filter(
                    approval_status=approval_status, department=department).all()
                event_requirements = Requirement.objects.filter(
                    approval_status=approval_status, event__in=events).all()
                requirements = dept_requirements.union(event_requirements)
                serialized = RequirementSerializer(requirements, many=True)
                return Response(
                    serialized.data,
                    status=status.HTTP_200_OK
                )
            except Department.DoesNotExist:
                return Response(
                    {"message": "Department not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        requirements = Requirement.objects.filter(
            approval_status=approval_status).all()
        serialized = RequirementSerializer(requirements, many=True)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except ApprovalStatus.DoesNotExist:
        return Response(
            {"message": "Status not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@authentication_classes([OAuth2Authentication])
def delete_my_requirement(request, req_id):
    try:
        requirement = Requirement.objects.get(id=req_id)
        if requirement.author == request.user:
            requirement.delete()
            return Response(
                {"message": "Requirement deleted"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "You are not authorized to delete this requirement"},
                status=status.HTTP_403_FORBIDDEN
            )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
# @has_perms(['delete_requirement'])
@has_requirement_perms(['delete_requirement'])
def delete_requirement(request, req_id):
    data = request.data
    id = data.get("dept_id")
    event_id = data.get("event_id")
    try:
        requirement = Requirement.objects.get(id=req_id)
        dept = requirement.department
        event = requirement.event
        if (event and event_id and event.id != event_id) or (dept and id and dept.id != id):
            return Response(
                {"message": "Requirement not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        requirement.delete()
        return Response(
            {"message": "Requirement deleted"},
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@authentication_classes([OAuth2Authentication])
def update_my_requirement(request, req_id):
    data = request.data
    try:
        requirement = Requirement.objects.get(id=req_id)
        pending = ApprovalStatus.objects.get(name="pending")
        first_approved = ApprovalStatus.objects.get(
            name="first_level_approved")
        second_approved = ApprovalStatus.objects.get(
            name="second_level_approved")
        final_approved = ApprovalStatus.objects.get(
            name="final_level_approved")
        if requirement.author != request.user:
            return Response(
                {"message": "You are not authorized to update this requirement"},
                status=status.HTTP_403_FORBIDDEN
            )
        if requirement.approval_status in [first_approved, second_approved, final_approved]:
            return Response(
                {"message": "You cannot update a requirement that has been approved"},
                status=status.HTTP_403_FORBIDDEN
            )
        new_unit_of_measure = UnitOfMeasure.objects.get_or_create(
            name=data.get("unit_of_measure").lower())[0]
        new_category, ctg_created = ResourceCategory.objects.get_or_create(
            name=data.get("category", "other").lower())
        new_resource, created = Resource.objects.get_or_create(name=data.get(
            "resource").lower(), unit_of_measure=new_unit_of_measure)
        if created:
            new_resource.category = new_category
            new_resource.save()
        requirement.resource = new_resource
        requirement.quantity = data.get("quantity", requirement.quantity)
        requirement.description = data.get(
            "description", requirement.description)
        requirement.approval_status = pending
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['change_requirement'])
def update_requirement(request, req_id):
    data = request.data
    id = data.get("dept_id")
    event_id = data.get("event_id")
    try:
        requirement = Requirement.objects.get(id=req_id)
        pending = ApprovalStatus.objects.get(name="pending")
        dept = requirement.department
        event = requirement.event
        if (event and event.id != event_id) or (dept and dept.id != id):
            return Response(
                {"message": "Requirement not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        new_unit_of_measure = UnitOfMeasure.objects.get_or_create(
            name=data.get("unit_of_measure").lower())[0]
        new_resource = Resource.objects.get_or_create(name=data.get(
            "resource").lower(), unit_of_measure=new_unit_of_measure)[0]
        requirement.resource = new_resource
        requirement.quantity = data.get("quantity", requirement.quantity)
        requirement.description = data.get(
            "description", requirement.description)
        requirement.approval_status = pending
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['first_level_req_approval'])
def dept_core_approve_requirement(request, req_id):
    data = request.data
    message = data.get("message")
    try:
        requirement = Requirement.objects.get(id=req_id)
        requirement.approval_status = ApprovalStatus.objects.get(
            name=f"first_level_approved")
        requirement.message = message
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['first_level_req_rejection'])
def dept_core_decline_requirement(request, req_id):
    data = request.data
    message = data.get("message")
    if not message:
        return Response(
            {"message": "Please provide a message for declining the requirement"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        requirement = Requirement.objects.get(id=req_id)
        requirement.approval_status = ApprovalStatus.objects.get(
            name="first_level_rejected")
        requirement.message = message
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['second_level_req_approval'])
def fr_super_coord_approve_requirement(request, req_id):
    data = request.data
    message = data.get("message")
    source = data.get("source")
    print(source)
    if source not in ["self_arranged", "fr_arranged"]:
        return Response(
            {"message": "Please provide a valid source for the requirement, either 'self_arranged' or 'fr_arranged'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        requirement = Requirement.objects.get(id=req_id)
        requirement.approval_status = ApprovalStatus.objects.get(
            name="second_level_approved")
        requirement.message = message
        requirement.arrangement_source = source
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['second_level_req_rejection'])
def fr_super_coord_decline_requirement(request, req_id):
    data = request.data
    message = data.get("message")
    if not message:
        return Response(
            {"message": "Please provide a message for declining the requirement"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        requirement = Requirement.objects.get(id=req_id)
        requirement.approval_status = ApprovalStatus.objects.get(
            name="second_level_rejected")
        requirement.message = message
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['final_level_req_approval'])
def fr_core_approve_requirement(request, req_id):
    data = request.data
    message = data.get("message")
    source = data.get("source")
    if source not in ["self_arranged", "fr_arranged"]:
        return Response(
            {"message": "Please provide a valid source for the requirement, either 'self_arranged' or 'fr_arranged'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        requirement = Requirement.objects.get(id=req_id)
        requirement.approval_status = ApprovalStatus.objects.get(
            name="final_level_approved")
        requirement.message = message
        requirement.arrangement_source = source
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except ApprovalStatus.DoesNotExist:
        return Response(
            {"message": "Invalid action, please use either 'approved' or 'declined'"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_requirement_perms(['final_level_req_rejection'])
def fr_core_decline_requirement(request, req_id):
    data = request.data
    message = data.get("message")
    if not message:
        return Response(
            {"message": "Please provide a message for declining the requirement"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        requirement = Requirement.objects.get(id=req_id)
        requirement.approval_status = ApprovalStatus.objects.get(
            name="final_level_rejected")
        requirement.message = message
        requirement.save()
        serialized = RequirementSerializer(requirement)
        return Response(
            serialized.data,
            status=status.HTTP_200_OK
        )
    except Requirement.DoesNotExist:
        return Response(
            {"message": "Requirement not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
def assign_fr_roles(request):
    fr_core = Group.objects.get(name='fr_core')
    if fr_core not in request.user.groups.all():
        return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    data = request.data
    name = data.get('name')
    if name not in ['fr_core', 'fr_super_coordinator', 'fr_coordinator', 'fr_volunteer', 'fr_coordinator']:
        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
    members = data.get('members')
    try:
        group = Group.objects.get(name=name)
    except Group.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    member_objects = []
    for member in members:
        try:
            member_objects.append(User.objects.get(email=member))
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    for member in member_objects:
        member.groups.add(group)
    return Response({'message': 'Roles created'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
def remove_fr_roles(request):
    fr_core = Group.objects.get(name='fr_core')
    if fr_core not in request.user.groups.all():
        return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    data = request.data
    name = data.get('name')
    if name not in ['fr_core', 'fr_super_coordinator', 'fr_coordinator', 'fr_volunteer', 'fr_coordinator']:
        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
    members = data.get('members')
    try:
        group = Group.objects.get(name=name)
    except Group.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    member_objects = []
    for member in members:
        try:
            member_objects.append(User.objects.get(email=member))
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    for member in member_objects:
        member.groups.remove(group)
    return Response({'message': 'Roles removed'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
def add_fr_role_perms(request):
    fr_core = Group.objects.get(name='fr_core')
    if fr_core not in request.user.groups.all():
        return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    data = request.data
    name = data.get('name')
    perms = data.get('perms')
    if name not in ['fr_core', 'fr_super_coordinator', 'fr_coordinator', 'fr_volunteer', 'fr_coordinator']:
        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(name=name)
    except Group.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    perms_objects = []
    for perm in perms:
        try:
            perms_objects.append(Permission.objects.get(codename=perm))
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    group.permissions.add(*perms_objects)
    return Response({'message': 'Permissions added'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
def remove_fr_role_perms(request):
    fr_core = Group.objects.get(name='fr_core')
    if fr_core not in request.user.groups.all():
        return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    data = request.data
    name = data.get('name')
    perms = data.get('perms')
    if name not in ['fr_core', 'fr_super_coordinator', 'fr_coordinator', 'fr_volunteer', 'fr_coordinator']:
        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(name=name)
    except Group.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    perms_objects = []
    for perm in perms:
        try:
            perms_objects.append(Permission.objects.get(codename=perm))
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    group.permissions.remove(*perms_objects)
    return Response({'message': 'Permissions removed'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
def get_fr_perms(request):
    core_perm = Permission.objects.filter(
        codename='fr_core_manage_requirement').first()
    super_perm = Permission.objects.filter(
        codename='fr_super_coordinator_manage_requirement').first()
    core_groups = Group.objects.filter(permissions=core_perm).all()
    super_groups = Group.objects.filter(permissions=super_perm).all()
    core_role_names = [group.name for group in core_groups]
    super_role_names = [group.name for group in super_groups]
    r = [
        {
            "title": "Final Approval/Rejection",
            "description": "Responsible for reviewing and granting ultimate approval or rejection to requirements ensuring adherence to criteria and orgazational standards",
            "name": "fr_core_manage_requirement",
            "roles": core_role_names
        },
        {
            "title": "Primary Approval/Rejection",
            "description": "Reviews, approves or rejects requirements prior to final approval ensuring compliance and alignment with criteria and orgazational standards",
            "name": "fr_super_coordinator_manage_requirement",
            "roles": super_role_names
        }
    ]
    return Response(r, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_requirement_perms(['view_requirement'])
def download_req_csv(request):
    requirements = Requirement.objects.prefetch_related(
        'resource',
        'resource__category',
        'resource__unit_of_measure',
        'department',
        'sub_department',
        'event',
        'approval_status',
        'author'
    ).all().order_by('id')

    data = []
    for req in requirements:
        data.append({
            "id": req.id,
            "resource": req.resource.name,
            "category": req.resource.category.name,
            "unit_of_measure": req.resource.unit_of_measure.name,
            "quantity": req.quantity,
            "description": req.description,
            "arrangement_source": req.arrangement_source,
            "department": req.department.name if req.department else None,
            "sub_department": req.sub_department.name if req.sub_department else None,
            "event": req.event.name if req.event else None,
            "approval_status": req.approval_status.name,
            "author": req.author.email,
            "updated_at": req.updated_at,

        })

    keys = data[0].keys()
    with open('requirements.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    with open('requirements.csv', 'rb') as file:
        response = HttpResponse(file.read(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=requirements.csv'
        return response
