from typing import OrderedDict
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.contrib.contenttypes.models import ContentType
from .models import Form, Input, Textarea, CheckboxGroup, Select, RadioGroup, Block, Dependency, Element


class InputSerializer(ModelSerializer):
    maxLength = SerializerMethodField()
    minLength = SerializerMethodField()

    class Meta:
        model = Input
        fields = [
            'id',
            'value',
            'required',
            'placeholder',
            'autocomplete',
            'max',
            'min',
            'maxLength',
            'minLength',
        ]

    def get_maxLength(self, obj):
        return obj.max_length

    def get_minLength(self, obj):
        return obj.min_length


class TextareaSerializer(ModelSerializer):
    class Meta:
        model = Textarea
        exclude = ['uuid', 'created_at', 'updated_at']


class CheckboxGroupSerializer(ModelSerializer):
    class Meta:
        model = CheckboxGroup
        exclude = ['uuid', 'created_at', 'updated_at']


class SelectSerializer(ModelSerializer):
    class Meta:
        model = Select
        exclude = ['uuid', 'created_at', 'updated_at']


class RadioGroupSerializer(ModelSerializer):
    class Meta:
        model = RadioGroup
        exclude = ['uuid', 'created_at', 'updated_at']


class ElementSerializer(ModelSerializer):
    element = SerializerMethodField()
    inputType = SerializerMethodField()
    block_id = SerializerMethodField()

    class Meta:
        model = Element
        fields = ['id', 'name', 'block_id', 'label',
                  'position', 'element', 'inputType', 'show']

    def get_block_id(self, obj):
        return obj.block.id

    def get_element(self, obj):
        input_type = ContentType.objects.get_for_model(Input)
        text_area_type = ContentType.objects.get_for_model(Textarea)
        check_box_type = ContentType.objects.get_for_model(CheckboxGroup)
        select_type = ContentType.objects.get_for_model(Select)
        radio_type = ContentType.objects.get_for_model(RadioGroup)
        content_type = obj.content_type
        if content_type == input_type:
            return InputSerializer(obj.content_object).data
        elif content_type == text_area_type:
            return TextareaSerializer(obj.content_object).data
        elif content_type == check_box_type:
            return CheckboxGroupSerializer(obj.content_object).data
        elif content_type == select_type:
            return SelectSerializer(obj.content_object).data
        elif content_type == radio_type:
            return RadioGroupSerializer(obj.content_object).data

    def get_inputType(self, obj):
        input_type = ContentType.objects.get_for_model(Input)
        text_area_type = ContentType.objects.get_for_model(Textarea)
        check_box_type = ContentType.objects.get_for_model(CheckboxGroup)
        select_type = ContentType.objects.get_for_model(Select)
        radio_type = ContentType.objects.get_for_model(RadioGroup)
        content_type = obj.content_type
        print(content_type)
        if content_type == input_type:
            input = obj.content_object
            return input.input_type
        elif content_type == text_area_type:
            return "textarea"
        elif content_type == check_box_type:
            return "checkbox"
        elif content_type == select_type:
            return "select"
        elif content_type == radio_type:
            return "radio"


class DependencySerializer(ModelSerializer):
    input = SerializerMethodField()
    select = SerializerMethodField()
    checkbox_group = SerializerMethodField()
    radio_group = SerializerMethodField()

    class Meta:
        model = Dependency
        fields = [
            'id',
            'name',
            'block',
            'value',
            'input',
            'select',
            'checkbox_group',
            'radio_group',
            'created_at',
            'updated_at'
        ]

    def get_input(self, obj):
        input_type = ContentType.objects.get_for_model(Input)
        if obj.content_type == input_type:
            return obj.object_id
        return None

    def get_select(self, obj):
        select_type = ContentType.objects.get_for_model(Select)
        if obj.content_type == select_type:
            return obj.object_id
        return None

    def get_checkbox_group(self, obj):
        checkbox_group_type = ContentType.objects.get_for_model(CheckboxGroup)
        if obj.content_type == checkbox_group_type:
            return obj.object_id
        return None

    def get_radio_group(self, obj):
        radio_group_type = ContentType.objects.get_for_model(RadioGroup)
        if obj.content_type == radio_group_type:
            return obj.object_id
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return OrderedDict([(key, ret[key]) for key in ret if ret[key] is not None])


class BlockSerializer(ModelSerializer):
    elements = SerializerMethodField()

    class Meta:
        model = Block
        fields = [
            'id',
            'form',
            'title',
            'position',
            'elements'
        ]

    def get_elements(self, obj):
        elements = Element.objects.filter(block=obj).order_by('position').all()
        return ElementSerializer(elements, many=True).data


class FormSerializer(ModelSerializer):
    blocks = SerializerMethodField()
    bg_img = SerializerMethodField()
    desc = SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            'id',
            'name',
            'desc',
            'blocks',
            'user',
            'published',
            'bg_img'
        ]

    def get_blocks(self, obj):
        blocks = Block.objects.filter(form=obj).order_by('position').all()
        return BlockSerializer(blocks, many=True).data

    def get_bg_img(self, obj):
        return obj.bg_image

    def get_desc(self, obj):
        return obj.description


class FormEditSerializer(ModelSerializer):
    class Meta:
        model = Form
        fields = '__all__'
