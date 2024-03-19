from django.db import models
from core.models import Event


class Round(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='rounds')
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.event.name + " - " + self.name


class SomeDude(models.Model):

    dude_type_choices = [
        ('speaker', 'Speaker'),
        ('judge', 'Judge'),
        ('mentor', 'Mentor'),
        ('Panelist', 'Panelist')
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    dude_type = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='some_dudes', null=True, blank=True)
    image = models.ImageField(upload_to='some_dudes')
    bio = models.TextField()

    def __str__(self):
        return self.name
