from typing import OrderedDict
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.contrib.contenttypes.models import ContentType
from .models import Form, Input, Textarea, CheckboxGroup, Select, RadioGroup, Block, Dependency


class InputSerializer(ModelSerializer):
    class Meta:
        model = Input
        fields = '__all__'


class TextareaSerializer(ModelSerializer):
    class Meta:
        model = Textarea
        fields = '__all__'


class CheckboxGroupSerializer(ModelSerializer):
    class Meta:
        model = CheckboxGroup
        fields = '__all__'


class SelectSerializer(ModelSerializer):
    class Meta:
        model = Select
        fields = '__all__'


class RadioGroupSerializer(ModelSerializer):
    class Meta:
        model = RadioGroup
        fields = '__all__'


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
    inputs = SerializerMethodField()
    checkbox_groups = SerializerMethodField()
    selects = SerializerMethodField()
    radio_groups = SerializerMethodField()
    textareas = SerializerMethodField()
    dependencies = SerializerMethodField()

    class Meta:
        model = Block
        fields = [
            'id',
            'form',
            'title',
            'position',
            'created_at',
            'updated_at',
            'inputs',
            'textareas',
            'checkbox_groups',
            'selects',
            'radio_groups',
            'dependencies'
        ]

    def get_inputs(self, obj):
        inputs = Input.objects.filter(block=obj).order_by('position').all()
        return InputSerializer(inputs, many=True).data

    def get_textareas(self, obj):
        textareas = Textarea.objects.filter(
            block=obj).order_by('position').all()
        return TextareaSerializer(textareas, many=True).data

    def get_checkbox_groups(self, obj):
        checkbox_groups = CheckboxGroup.objects.filter(
            block=obj).order_by('position').all()
        return CheckboxGroupSerializer(checkbox_groups, many=True).data

    def get_selects(self, obj):
        selects = Select.objects.filter(block=obj).order_by('position').all()
        return SelectSerializer(selects, many=True).data

    def get_radio_groups(self, obj):
        radio_groups = RadioGroup.objects.filter(
            block=obj).order_by('position').all()
        return RadioGroupSerializer(radio_groups, many=True).data

    def get_dependencies(self, obj):
        dependencies = Dependency.objects.filter(
            block=obj).all()
        return DependencySerializer(dependencies, many=True).data


class FormSerializer(ModelSerializer):
    blocks = SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at',
            'blocks'
            'user',
            'published',
            'bg_image'
        ]

    def get_blocks(self, obj):
        blocks = Block.objects.filter(form=obj).order_by('position').all()
        return BlockSerializer(blocks, many=True).data
