from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from core.models import Student, Event, Department
from core.serializers import EventSerializer
from forms.types import FormType, SelectType, RadioGroupType, ElementType, InputType, BlockType, CheckboxGroupType
from .models import Round, SomeDude
from .serializers import RoundSerializer
from utils.decorators import has_perms, authed
from .decorators import has_event_perms
from datetime import datetime

from forms.models import Element, Form, Block, Input, Select, Textarea, RadioGroup, Dependency, CheckboxGroup
from forms.serializers import FormSerializer, BlockSerializer, InputSerializer, SelectSerializer, TextareaSerializer, RadioGroupSerializer, DependencySerializer, CheckboxGroupSerializer
from forms.serializers import FormSerializer


@api_view(['POST'])
@has_event_perms(['add_event'])
def add_event(request):
    user = request.user
    data = request.data
    dept_id = data.get('dept_id')
    event_name = data.get('event_name')
    head_email = data.get('head_email')
    is_team_event = data.get('is_team_event')
    max_team_size = data.get('max_team_size')
    min_team_size = data.get('min_team_size')
    max_participants = data.get('max_participants')
    fee = data.get('fee')
    description = data.get('description')
    location = data.get('location')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    registration_start_date = datetime.strptime(
        data.get('registration_start_date'), '%Y-%m-%d %H:%M:%S')
    registration_end_date = datetime.strptime(
        data.get('registration_end_date'), '%Y-%m-%d %H:%M:%S')
    try:
        user = User.objects.get(email=head_email)
        dept = Department.objects.get(id=dept_id)
        if not dept.event_based:
            return Response({'message': 'Department is not event based'}, status=status.HTTP_400_BAD_REQUEST)
        event = Event.objects.create(
            name=event_name,
            head=user,
            department=dept,
            is_team_event=is_team_event,
            max_team_size=max_team_size,
            min_team_size=min_team_size,
            max_participants=max_participants,
            fee=fee if fee else 0,
            description=description,
            location=location,
            start_date=start_date,
            end_date=end_date,
            registration_start_date=registration_start_date,
            registration_end_date=registration_end_date
        )
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'message': 'User with the provided email not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Department.DoesNotExist:
        return Response({'message': 'Department with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['change_event'])
def edit_event(request):
    data = request.data
    event_id = data.get('event_id')
    event = Event.objects.get(id=event_id)
    event_name = data.get('event_name')
    head_email = data.get('head_email')
    is_team_event = data.get('is_team_event')
    max_team_size = data.get('max_team_size')
    min_team_size = data.get('min_team_size')
    max_participants = data.get('max_participants')
    fee = data.get('fee')
    description = data.get('description')
    location = data.get('location')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
    registration_start_date = datetime.strptime(
        data.get('registration_start_date'), '%Y-%m-%d %H:%M:%S')
    registration_end_date = datetime.strptime(
        data.get('registration_end_date'), '%Y-%m-%d %H:%M:%S')
    try:
        user = User.objects.get(email=head_email)
        event.name = event_name
        event.head = user
        event.is_team_event = is_team_event
        event.max_team_size = max_team_size
        event.min_team_size = min_team_size
        event.max_participants = max_participants
        event.fee = fee if fee else 0
        event.description = description
        event.location = location
        event.start_date = start_date
        event.end_date = end_date
        event.registration_start_date = registration_start_date
        event.registration_end_date = registration_end_date
        event.is_approved = False
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': 'User with the provided email not found'}, status=status.HTTP_400_BAD_REQUEST)


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
        event = Event.objects.get(id=event_id)
        event.is_approved = True
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event with the provided id not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@has_event_perms(['approve_event'])
def disapprove_event(request):
    data = request.data
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        event.is_approved = False
        event.save()
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
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
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
    description = data.get('description')
    try:
        event = Event.objects.get(id=event_id)
        round = Round.objects.create(
            event=event,
            name=round_name,
            start_time=start_date,
            end_time=end_date,
            location=location,
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
    description = data.get('description')
    try:
        event = Event.objects.get(id=event_id)
        round = Round.objects.get(id=round_id)
        round.name = round_name
        round.start_time = start_time
        round.end_time = end_time
        round.location = location
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
    bg_image = data.get('bg_image')
    event_id = data.get('event_id')
    try:
        event = Event.objects.get(id=event_id)
        with transaction.atomic():
            form = Form.objects.create(
                name=form_name,
                description=form_description,
                bg_image=bg_image,
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
    form_data: FormType = data.get('form')
    blocks = form_data.blocks
    try:
        event = Event.objects.get(id=event_id)
        form = event.form
        if not form:
            return Response({'message': 'Form not found'}, status=status.HTTP_400_BAD_REQUEST)
        form.name = data.get('name')
        form.description = data.get('description')
        form.bg_image = data.get('bg_image')
        form.save()
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
                )
            elements = block.elements
            for element in elements:
                try:
                    el_object = Element.objects.get(uuid=element.id)
                    el_type = element.inputType
                    actual_type = "input"
                    input_conent_type = ContentType.objects.get_for_model(
                        Input)
                    if el_type == "select":
                        actual_type = "select"
                        input_conent_type = ContentType.objects.get_for_model(
                            Select)
                        if not isinstance(element.element, SelectType):
                            return Response(
                                {'message': 'Element is not a select'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        select_child: SelectType = element.element
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
                        if not isinstance(element.element, RadioGroupType):
                            return Response(
                                {'message': 'Element is not a radio'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        radio_child: RadioGroupType = element.element
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
                        if not isinstance(element.element, CheckboxGroupType):
                            return Response(
                                {'message': 'Element is not a checkbox'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        checkbox_child: CheckboxGroupType = element.element
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

                    elif el_type == "input":
                        actual_type = "input"
                        input_conent_type = ContentType.objects.get_for_model(
                            Input)
                        if not isinstance(element.element, InputType):
                            return Response(
                                {'message': 'Element is not a input'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        input_child: InputType = element.element
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
                    else:
                        return Response(
                            {'message': 'Element type not supported'}, status=status.HTTP_400_BAD_REQUEST
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
                        if not isinstance(element.element, SelectType):
                            return Response(
                                {'message': 'Element is not a select'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        select_child: SelectType = element.element
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
                        if not isinstance(element.element, RadioGroupType):
                            return Response(
                                {'message': 'Element is not a radio'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        radio_child: RadioGroupType = element.element
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
                        if not isinstance(element.element, CheckboxGroupType):
                            return Response(
                                {'message': 'Element is not a checkbox'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        checkbox_child: CheckboxGroupType = element.element
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

                    elif el_type == "input":
                        actual_type = "input"
                        input_conent_type = ContentType.objects.get_for_model(
                            Input)
                        if not isinstance(element.element, InputType):
                            return Response(
                                {'message': 'Element is not a input'}, status=status.HTTP_400_BAD_REQUEST
                            )
                        input_child: InputType = element.element
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
                    else:
                        return Response(
                            {'message': 'Element type not supported'}, status=status.HTTP_400_BAD_REQUEST
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
