from django.db import models
from django.contrib.auth.models import User
from core.models import Event, Student


class Round(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='rounds')
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    location_link = models.URLField(null=True, blank=True, max_length=2048)
    description = models.TextField()

    def __str__(self):
        return self.event.name + " - " + self.name


class SomeDude(models.Model):

    dude_type_choices = [
        ('speaker', 'Speaker'),
        ('judge', 'Judge'),
        ('mentor', 'Mentor'),
        ('panelist', 'Panelist')
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    dude_type = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='some_dudes', null=True, blank=True)
    image = models.URLField(max_length=2048, null=True, blank=True)
    bio = models.TextField()

    def __str__(self):
        return self.name


class RegData(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event.name + " - " + self.student.email
