from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import Permission
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from core.models import FAQ, Action, ApprovalStatus, Link, Sponsor, Event, Department
from forms.types import FormType, SelectType, RadioGroupType, ElementType, InputType, BlockType, CheckboxGroupType
from .models import RegData, Round, SomeDude
from .serializers import RoundSerializer, EventSerializer, SimpleEventSerializer
from utils.decorators import has_perms, authed
from .decorators import has_event_perms
from datetime import datetime, timezone, timedelta
import csv
from forms.models import Element, Form, Block, Input, Select, RadioGroup, CheckboxGroup
from forms.serializers import FormSerializer
from forms.serializers import FormSerializer
from typing import Dict


@api_view(['POST'])
@has_event_perms(['add_event'])
def add_event(request):
    user = request.user
    data = request.data
    dept_id = data.get('dept_id')
    event_name = data.get('name')
    head_email = data.get('head')
    try:
        dept = Department.objects.get(id=dept_id)
        if not dept.event_based:
            return Response({'message': 'Department is not event based'}, status=status.HTTP_400_BAD_REQUEST)
        head = User.objects.get(email=head_email)
        event = Event.objects.create(
            name=event_name,
            department=dept,
            head=head,
            created_by=user
        )
        req_codenames = ["view_requirement", "add_requirement",
                         "view_bill", "add_bill", "change_event"]
        permissions = Permission.objects.filter(
            codename__in=req_codenames).all()
        event.permissions.add(*permissions)
        event.save()

        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'message': 'User with the provided email not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Department.DoesNotExist:
        return Response({'message': 'Department with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['manage_event_member'])
def add_event_members(request):
    data = request.data
    event_id = data.get('event_id')
    members = data.get('members')
    try:
        event = Event.objects.get(id=event_id)
        users = User.objects.filter(email__in=members).all()
        event.members.add(*users)
        event.save()
        return Response({'message': 'Members added successfully'}, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['change_event'])
def edit_event(request):
    data = request.data
    event_id = data.get('event_id')
    event_name = data.get('name')
    is_team_event = data.get('is_team_event')
    max_team_size = data.get('max_team_size')
    min_team_size = data.get('min_team_size')
    max_participants = data.get('max_participants')
    fee = data.get('fee')
    description = data.get('description')
    location = data.get('location')
    location = data.get('location')
    location_link = data.get('location_link')
    start_date = datetime.fromtimestamp(
        int(data.get('start_date'))//1000).replace(tzinfo=timezone.utc) - timedelta(hours=5, minutes=30)
    end_date = datetime.fromtimestamp(
        int(data.get('end_date'))//1000).replace(tzinfo=timezone.utc) - timedelta(hours=5, minutes=30)
    registration_start_date = datetime.fromtimestamp(
        int(data.get('registration_start_date'))//1000).replace(tzinfo=timezone.utc) - timedelta(hours=5, minutes=30)
    registration_end_date = datetime.fromtimestamp(
        int(data.get('registration_end_date'))//1000).replace(tzinfo=timezone.utc) - timedelta(hours=5, minutes=30)
    rules = data.get('rules')
    sponsors = data.get('sponsors')
    rounds = data.get('rounds')
    social_links = data.get('social_links')
    faqs = data.get('faqs')
    some_dudes = data.get('some_dudes')
    try:
        event = Event.objects.get(id=event_id)
        event.name = event_name if event_name else event.name
        event.is_team_event = is_team_event
        event.max_team_size = max_team_size
        event.min_team_size = min_team_size
        event.max_participants = max_participants
        event.fee = fee if fee else 0
        event.description = description
        event.location = location
        event.location_link = location_link
        event.start_date = start_date
        event.end_date = end_date
        event.registration_start_date = registration_start_date
        event.registration_end_date = registration_end_date
        event.rules = rules
        event.is_approved = False
        Action.objects.create(
            user=request.user,
            approval_status=ApprovalStatus.objects.get(name="pending"),
            message="event edited",
            content_type=ContentType.objects.get_for_model(Event),
            object_id=event.id
        )
        event.save()
        FAQ.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=event.id
        ).delete()
        Link.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=event.id
        ).delete()
        Round.objects.filter(
            event=event
        ).delete()
        Sponsor.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=event.id
        ).delete()
        SomeDude.objects.filter(
            event=event
        ).delete()
        for faq in faqs:
            FAQ.objects.create(
                question=faq.get('question'),
                answer=faq.get('answer'),
                content_type=ContentType.objects.get_for_model(Event),
                object_id=event.id
            )
        for link in social_links:
            Link.objects.create(
                name=link.get('name'),
                content_type=ContentType.objects.get_for_model(Event),
                object_id=event.id,
                url=link.get('url')
            )
        for round in rounds:
            Round.objects.create(
                event=event,
                name=round.get('name'),
                start_time=datetime.fromtimestamp(
                    int(round.get('start_time')) // 1000).replace(tzinfo=timezone.utc) - timedelta(hours=5, minutes=30),
                end_time=datetime.fromtimestamp(
                    int(round.get('end_time')) // 1000).replace(tzinfo=timezone.utc) - timedelta(hours=5, minutes=30),
                location=round.get('location'),
                location_link=round.get('location_link'),
                description=round.get('description')
            )
        for sponsor in sponsors:
            Sponsor.objects.create(
                name=sponsor.get('name'),
                title=sponsor.get('title'),
                logo=sponsor.get('logo'),
                url=sponsor.get('url'),
                content_type=ContentType.objects.get_for_model(Event),
                object_id=event.id
            )
        for some_dude in some_dudes:
            SomeDude.objects.create(
                name=some_dude.get('name'),
                email=some_dude.get('email'),
                dude_type=some_dude.get('dude_type'),
                event=event,
                image=some_dude.get('image'),
                bio=some_dude.get('bio'),

            )
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': 'User with the provided email not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@has_event_perms(['delete_event'])
def delete_event(request):
    data = request.data
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        return Response({'message': 'Event deleted successfully'}, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['approve_event'])
def approve_event(request):
    data = request.data
    event_id = data.get('event_id')
    try:
        with transaction.atomic():
            event = Event.objects.get(id=event_id)
            event.is_approved = True
            event.save()
            Action.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Event),
                object_id=event.id,
                approval_status=ApprovalStatus.objects.get(
                    name="final_level_approved"),
                message="Event approved"
            )
            try:
                from_email = f"Event Management <{settings.EMAIL_HOST_USER}>"
                to = event.head.email
                subject = 'Event Approved'
                text_content = f"Dear {event.head.first_name},\n\nYour event {event.name} has been approved. You can view the event on the website.\n Please note that any changes you make hereafter will have to go through approval again, and will be inactive until approved. \n\n Regards,\n Event Management."
                mail = EmailMultiAlternatives(
                    subject, text_content, from_email, [to])
                mail.send()
            except Exception as e:
                print(e)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['approve_event'])
def disapprove_event(request):
    data = request.data
    event_id = data.get('event_id')
    message = data.get('message')
    if not message:
        return Response({'message': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        with transaction.atomic():
            event = Event.objects.get(id=event_id)
            event.is_approved = False
            event.save()
            Action.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Event),
                object_id=event.id,
                approval_status=ApprovalStatus.objects.get(
                    name="final_level_rejected"),
                message=message
            )
            try:
                from_email = f"Event Management <{settings.EMAIL_HOST_USER}>"
                to = event.head.email
                subject = 'Event Rejected'
                text_content = f"Dear {event.head.first_name},\n\nYour event {event.name} has been rejected for the following reason:\n\n {message}.\n\n You can still view the event on the portal and make the necessary changes and wait for approval again. Until it is approved you event will remain inactive. If you think this was a mistake, you can contact your department core for further clarification\n\n Regards,\n Event Management."
                mail = EmailMultiAlternatives(
                    subject, text_content, from_email, [to])
                mail.send()
            except Exception as e:
                print(e)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authed()
def view_dept_events(request):
    data = request.GET
    dept_id = data.get('dept_id')
    try:
        dept = Department.objects.get(id=dept_id)
        events = Event.objects.filter(department=dept)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return Response({'message': 'Department with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authed()
def view_all_events(request):
    data = request.GET
    dept_id = data.get('dept_id')
    event_id = data.get('event_id')
    if not event_id and not dept_id:
        return Response({'message': 'Provide either event_id or dept_id'}, status=status.HTTP_400_BAD_REQUEST)
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            serializer = SimpleEventSerializer(event)
            return Response([serializer.data], status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)
    if dept_id:
        try:
            dept = Department.objects.get(id=dept_id)
            events = Event.objects.filter(department=dept)
            serializer = SimpleEventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'message': 'Department with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)
    events = Event.objects.all()
    serializer = SimpleEventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authed()
def view_event(request):
    data = request.GET
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@has_perms(['change_event'])
def add_round(request):
    data = request.data
    event_id = data.get('event_id')
    round_name = data.get('round_name')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    location = data.get('location')
    location_link = data.get('location_link')
    description = data.get('description')
    try:
        event = Event.objects.get(id=event_id)
        round = Round.objects.create(
            event=event,
            name=round_name,
            start_time=start_date,
            end_time=end_date,
            location=location,
            location_link=location_link,
            description=description
        )
        event.is_approved = False
        serializer = RoundSerializer(round)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_perms(['change_event'])
def edit_round(request):
    data = request.data
    event_id = data.get('event_id')
    round_id = data.get('round_id')
    round_name = data.get('round_name')
    start_time = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    location = data.get('location')
    location_link = data.get('location_link')
    description = data.get('description')
    try:
        event = Event.objects.get(id=event_id)
        round = Round.objects.get(id=round_id)
        round.name = round_name
        round.start_time = start_time
        round.end_time = end_time
        round.location = location
        round.location_link = location_link
        round.description = description
        round.save()
        event.is_approved = False
        serializer = RoundSerializer(round)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Round.DoesNotExist:
        return Response({'message': 'Round with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@has_perms(['change_event'])
def delete_round(request):
    data = request.data
    event_id = data.get('event_id')
    round_id = data.get('round_id')
    try:
        event = Event.objects.get(id=event_id)
        round = Round.objects.get(id=round_id)
        round.delete()
        event.is_approved = False
        return Response({'message': 'Round deleted successfully'}, status=status.HTTP_200_OK)
    except Round.DoesNotExist:
        return Response({'message': 'Round with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@has_perms(['change_event'])
def create_event_form(request):
    data = request.data
    user = request.user
    form_name = data.get('name')
    form_description = data.get('description')
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        if event.form:
            return Response({'message': 'Event already has a form'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            form = Form.objects.create(
                name=form_name,
                description=form_description,
                user=user,
                published=False
            )
            event.form = form
            event.save()
            serializer = FormSerializer(form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_perms(['change_event'])
def edit_event_form(request):
    data = request.data
    event_id = data.get('event_id')
    form_data = FormType.from_dict(data['form'])

    blocks = form_data.blocks
    try:
        event = Event.objects.get(id=event_id)
        form = event.form
        if not form:
            form = Form.objects.create(
                name=form_data.name,
                description=form_data.desc,
                user=request.user,
                published=False,
                bg_image=form_data.bg_img
            )
            event.form = form
            event.is_approved = False
            event.save()
            # return Response({'message': 'Form not found'}, status=status.HTTP_400_BAD_REQUEST)
        Action.objects.create(
            user=request.user,
            message="form edited",
            approval_status=ApprovalStatus.objects.get(name="pending"),
            content_type=ContentType.objects.get_for_model(Event),
            object_id=event.id
        )
        form.name = form_data.name
        form.description = form_data.desc
        form.bg_image = form_data.bg_img
        form.save()
        form_blocks = Block.objects.filter(form=form).all()
        user_block_ids = [block.id for block in blocks]
        for block in form_blocks:
            if block.uuid not in user_block_ids:
                block.delete()
        for block in blocks:
            block_id = block.id
            try:
                block_obj = Block.objects.get(uuid=block_id)
                block_obj.title = block.title
                block_obj.position = block.position
            except Block.DoesNotExist:
                block_obj = Block.objects.create(
                    uuid=block_id,
                    title=block.title,
                    position=block.position,
                    form=form
                )
            elements = block.elements
            user_element_ids = [element.id for element in elements]
            block_elements = Element.objects.filter(
                block=block_obj
            ).all()
            for element in block_elements:
                if element.uuid not in user_element_ids:
                    element.delete()
            for element in elements:
                try:
                    # print(f"element: {element}")
                    # print(type(element))
                    el_object = Element.objects.get(uuid=element.id)
                    el_type = element.inputType
                    actual_type = "input"
                    input_conent_type = ContentType.objects.get_for_model(
                        Input)
                    if el_type == "select":
                        actual_type = "select"
                        input_conent_type = ContentType.objects.get_for_model(
                            Select)
                        if not isinstance(ElementType.from_dict(
                                element.element,  # type: ignore
                                input_type="select"), SelectType):
                            return Response(
                                {'message': 'Element is not a select'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        select_child: SelectType = ElementType.from_dict(
                            element.element, input_type="select")    # type: ignore
                        try:
                            child_object = Select.objects.get(
                                uuid=select_child.id)
                            child_object.value = select_child.value
                            child_object.required = select_child.required
                            child_object.inputs = select_child.inputs
                            child_object.save()
                        except Select.DoesNotExist:
                            child_object = Select.objects.create(
                                uuid=select_child.id,
                                value=select_child.value,
                                required=select_child.required,
                                inputs=select_child.inputs
                            )

                    elif el_type == "radio":
                        actual_type = "radio"
                        input_conent_type = ContentType.objects.get_for_model(
                            RadioGroup)
                        if not isinstance(ElementType.from_dict(
                                element.element,  # type: ignore
                                input_type="radio"), RadioGroupType):
                            return Response(
                                {'message': 'Element is not a radio'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        radio_child: RadioGroupType = ElementType.from_dict(
                            element.element, input_type="radio")    # type: ignore
                        try:
                            child_object = RadioGroup.objects.get(
                                uuid=radio_child.id)
                            child_object.value = radio_child.value
                            child_object.required = radio_child.required
                            child_object.inputs = radio_child.inputs
                            child_object.save()
                        except RadioGroup.DoesNotExist:
                            child_object = RadioGroup.objects.create(
                                uuid=radio_child.id,
                                value=radio_child.value,
                                required=radio_child.required,
                                inputs=radio_child.inputs
                            )
                    elif el_type == "checkbox":
                        actual_type = "checkbox"
                        input_conent_type = ContentType.objects.get_for_model(
                            CheckboxGroup)
                        if not isinstance(ElementType.from_dict(
                                element.element,  # type: ignore
                                input_type="checkbox"), CheckboxGroupType):
                            return Response(
                                {'message': 'Element is not a checkbox'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        checkbox_child: CheckboxGroupType = ElementType.from_dict(
                            element.element, input_type="checkbox")    # type: ignore
                        try:
                            child_object = CheckboxGroup.objects.get(
                                uuid=checkbox_child.id)
                            child_object.values = checkbox_child.values
                            child_object.required = checkbox_child.required
                            child_object.inputs = checkbox_child.inputs
                            child_object.save()
                        except CheckboxGroup.DoesNotExist:
                            child_object = CheckboxGroup.objects.create(
                                uuid=checkbox_child.id,
                                values=checkbox_child.values,
                                required=checkbox_child.required,
                                inputs=checkbox_child.inputs
                            )

                    else:
                        actual_type = "input"
                        input_conent_type = ContentType.objects.get_for_model(
                            Input)
                        if isinstance(element.element, Dict) and not isinstance(ElementType.from_dict(element.element), InputType):
                            # print(element.element)
                            # print(type(element.element))
                            return Response(
                                {'message': 'Element is not a input'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        input_child = ElementType.from_dict(
                            element.element)    # type: ignore
                        try:
                            child_object = Input.objects.get(
                                uuid=input_child.id)
                            child_object.value = input_child.value
                            child_object.required = input_child.required
                            child_object.placeholder = input_child.placeholder
                            child_object.autocomplete = input_child.autocomplete
                            child_object.max = input_child.max
                            child_object.min = input_child.min
                            child_object.max_length = input_child.maxLength
                            child_object.min_length = input_child.minLength
                            child_object.input_type = element.inputType

                            child_object.save()
                        except Input.DoesNotExist:
                            child_object = Input.objects.create(
                                uuid=input_child.id,
                                value=input_child.value,
                                required=input_child.required,
                                placeholder=input_child.placeholder,
                                autocomplete=input_child.autocomplete,
                                max=input_child.max,
                                min=input_child.min,
                                max_length=input_child.maxLength,
                                min_length=input_child.minLength,
                                input_type=element.inputType
                            )
                    el_object.label = element.label
                    el_object.name = element.name
                    el_object.element_type = actual_type
                    el_object.position = element.position
                    el_object.content_type = input_conent_type
                    el_object.object_id = child_object.id
                    el_object.save()

                except Element.DoesNotExist:
                    el_type = element.inputType
                    actual_type = "input"
                    input_conent_type = ContentType.objects.get_for_model(
                        Input)
                    if el_type == "select":
                        actual_type = "select"
                        input_conent_type = ContentType.objects.get_for_model(
                            Select)
                        if not isinstance(ElementType.from_dict(
                                element.element,  # type: ignore
                                input_type="select"), SelectType):
                            return Response(
                                {'message': 'Element is not a select'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        select_child: SelectType = ElementType.from_dict(
                            element.element, input_type="select")    # type: ignore
                        try:
                            child_object = Select.objects.get(
                                uuid=select_child.id)
                            child_object.value = select_child.value
                            child_object.required = select_child.required
                            child_object.inputs = select_child.inputs
                            child_object.save()
                        except Select.DoesNotExist:
                            child_object = Select.objects.create(
                                uuid=select_child.id,
                                value=select_child.value,
                                required=select_child.required,
                                inputs=select_child.inputs
                            )

                    elif el_type == "radio":
                        actual_type = "radio"
                        input_conent_type = ContentType.objects.get_for_model(
                            RadioGroup)
                        if not isinstance(ElementType.from_dict(
                                element.element,    # type: ignore
                                input_type="radio"), RadioGroupType):
                            return Response(
                                {'message': 'Element is not a radio'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        radio_child: RadioGroupType = ElementType.from_dict(
                            element.element, input_type="radio")    # type: ignore
                        try:
                            child_object = RadioGroup.objects.get(
                                uuid=radio_child.id)
                            child_object.value = radio_child.value
                            child_object.required = radio_child.required
                            child_object.inputs = radio_child.inputs
                            child_object.save()
                        except RadioGroup.DoesNotExist:
                            child_object = RadioGroup.objects.create(
                                uuid=radio_child.id,
                                value=radio_child.value,
                                required=radio_child.required,
                                inputs=radio_child.inputs
                            )
                    elif el_type == "checkbox":
                        actual_type = "checkbox"
                        input_conent_type = ContentType.objects.get_for_model(
                            CheckboxGroup)
                        if not isinstance(ElementType.from_dict(
                                element.element,    # type: ignore
                                input_type="checkbox"),
                                CheckboxGroupType):
                            return Response(
                                {'message': 'Element is not a checkbox'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        checkbox_child: CheckboxGroupType = ElementType.from_dict(
                            element.element, input_type="checkbox")    # type: ignore
                        try:
                            child_object = CheckboxGroup.objects.get(
                                uuid=checkbox_child.id)
                            child_object.values = checkbox_child.values
                            child_object.required = checkbox_child.required
                            child_object.inputs = checkbox_child.inputs
                            child_object.save()
                        except CheckboxGroup.DoesNotExist:
                            child_object = CheckboxGroup.objects.create(
                                uuid=checkbox_child.id,
                                values=checkbox_child.values,
                                required=checkbox_child.required,
                                inputs=checkbox_child.inputs
                            )

                    else:
                        actual_type = "input"
                        input_conent_type = ContentType.objects.get_for_model(
                            Input)
                        if isinstance(element.element, Dict) and not isinstance(ElementType.from_dict(element.element), InputType):
                            # print(element.element)
                            # print(type(element.element))
                            return Response(
                                {'message': 'Element is not a input'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        input_child: InputType = ElementType.from_dict(
                            element.element)    # type: ignore
                        try:
                            child_object = Input.objects.get(
                                uuid=input_child.id)
                            child_object.value = input_child.value
                            child_object.required = input_child.required
                            child_object.placeholder = input_child.placeholder
                            child_object.autocomplete = input_child.autocomplete
                            child_object.max = input_child.max
                            child_object.min = input_child.min
                            child_object.max_length = input_child.maxLength
                            child_object.min_length = input_child.minLength
                            child_object.input_type = element.inputType

                            child_object.save()
                        except Input.DoesNotExist:
                            child_object = Input.objects.create(
                                uuid=input_child.id,
                                value=input_child.value,
                                required=input_child.required,
                                placeholder=input_child.placeholder,
                                autocomplete=input_child.autocomplete,
                                max=input_child.max,
                                min=input_child.min,
                                max_length=input_child.maxLength,
                                min_length=input_child.minLength,
                                input_type=element.inputType
                            )
                    el_object = Element.objects.create(
                        uuid=element.id,
                        label=element.label,
                        position=element.position,
                        block=block_obj,
                        name=element.name,
                        element_type=actual_type,
                        content_type=input_conent_type,
                        object_id=child_object.id
                    )

        serializer = FormSerializer(form)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authed()
def view_form(request):
    data = request.GET
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        if not event.form:
            return Response({'message': 'Event has no form'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FormSerializer(event.form)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@has_event_perms(['view_event_reg_data'])
def view_event_reg_data(request):
    data = request.GET
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        data = []
        reg_data = RegData.objects.prefetch_related(
            'student').filter(event=event).all()
        for reg in reg_data:
            user = User.objects.filter(email=reg.student.email).first()
            if not user:
                continue
            d = {}
            d['user'] = {}
            d['user']['id'] = user.id  # type: ignore
            d['user']['name'] = f"{user.first_name} {user.last_name}"
            d['user']['email'] = user.email
            d['data'] = [reg.data[key] for key in reg.data.keys()]
            data.append(d)
        return Response(data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@has_event_perms(['view_event_reg_data'])
def get_csv_data(request):
    data = request.GET
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        data = []
        reg_data = RegData.objects.prefetch_related(
            'student').filter(event=event).all()
        for reg in reg_data:
            user = User.objects.filter(email=reg.student.email).first()
            if not user:
                continue
            d = {}
            d['user'] = {}
            d['user']['name'] = f"{user.first_name} {user.last_name}"
            d['user']['email'] = user.email
            d['data'] = reg.data
            data.append(d)
        cols = ['name', 'email']
        sample = data[0]
        for key in sample["data"]:
            cols.append(sample["data"][key]["label"])
        values = []
        for d in data:
            row = [d["user"]["name"], d["user"]["email"]]
            for key in d["data"]:
                row.append(d["data"][key]["value"])
            values.append(row)
        with open('reg_data.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            writer.writerows(values)
        with open('reg_data.csv', 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=reg_data.csv'
            return response

    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)
