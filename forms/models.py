from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
import uuid


class Form(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bg_image = models.URLField(max_length=2048, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Block(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore
        ordering = ['position']

    def __str__(self):
        return str(self.form) + ' - ' + self.title


class Element(models.Model):
    element_types = (
        ('input', 'Input'),
        ('textarea', 'Textarea'),
        ('select', 'Select'),
        ('checkbox_group', 'Checkbox Group'),
        ('radio_group', 'Radio Group'),
    )
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    name = models.CharField(max_length=128)
    position = models.IntegerField()
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    label = models.CharField(max_length=1024)
    element_type = models.CharField(max_length=128)
    show = models.BooleanField(default=False)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.block) + ' - ' + self.label


class Input(models.Model):

    INPUT_TYPES = (
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('password', 'Password'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime-local', 'Datetime Local'),
        ('file', 'File'),
        ('color', 'Color'),
        ('tel', 'Tel'),
        ('url', 'Url'),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    input_type = models.CharField(max_length=128, choices=INPUT_TYPES)
    required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=128, null=True, blank=True)
    autocomplete = models.BooleanField(default=False)
    max_length = models.IntegerField(null=True, blank=True)
    min_length = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    min = models.IntegerField(null=True, blank=True)
    value = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        content_type = ContentType.objects.get_for_model(Input)
        element = Element.objects.filter(
            content_type=content_type, object_id=self.id).first()
        return str(element.block) + ' - ' + element.label if element else ''


class Textarea(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=128, null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    min_length = models.IntegerField(null=True, blank=True)
    rows = models.IntegerField(null=True, blank=True)
    cols = models.IntegerField(null=True, blank=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        content_type = ContentType.objects.get_for_model(Textarea)
        element = Element.objects.filter(
            content_type=content_type, object_id=self.id).first()
        return str(element.block) + ' - ' + element.label if element else ''


class RadioGroup(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    inputs = models.JSONField()
    value = models.CharField(max_length=1024, null=True, blank=True)
    required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        content_type = ContentType.objects.get_for_model(RadioGroup)
        element = Element.objects.filter(
            content_type=content_type, object_id=self.id).first()
        return str(element.block) + ' - ' + element.label if element else ''


class CheckboxGroup(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    inputs = models.JSONField()
    values = models.JSONField(default=list)
    required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        content_type = ContentType.objects.get_for_model(CheckboxGroup)
        element = Element.objects.filter(
            content_type=content_type, object_id=self.id).first()
        return str(element.block) + ' - ' + element.label if element else ''


class Select(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    inputs = models.JSONField()
    value = models.CharField(max_length=1024, null=True, blank=True)
    required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        content_type = ContentType.objects.get_for_model(Select)
        element = Element.objects.filter(
            content_type=content_type, object_id=self.id).first()
        return str(element.block) + ' - ' + element.label if element else ''


class Dependency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    value = models.CharField(max_length=128)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.block) + ' - ' + self.value
