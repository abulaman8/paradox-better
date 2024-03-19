from django.db import models
from django.contrib.auth.models import User


class Form(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bg_image = models.ImageField(
        upload_to='form_bg_images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Block(models.Model):
    id = models.AutoField(primary_key=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Input(models.Model):

    INPUT_TYPES = (
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('password', 'Password'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime-local', 'Datetime-local'),
        ('file', 'File'),
        ('color', 'Color'),
        ('tel', 'Tel'),
        ('url', 'Url'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    label = models.CharField(max_length=128)
    input_type = models.CharField(max_length=128, choices=INPUT_TYPES)
    position = models.IntegerField()
    required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=128, null=True, blank=True)
    autocomplete = models.BooleanField(default=False)
    max_length = models.IntegerField(null=True, blank=True)
    min_length = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    min = models.IntegerField(null=True, blank=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RadioGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    label = models.CharField(max_length=128)
    inputs = models.JSONField()
    value = models.CharField(max_length=128, null=True, blank=True)
    position = models.IntegerField()
    required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
