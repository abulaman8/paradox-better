from django.db import models
from django.contrib.auth.models import User
from core.models import Event, Student


class SrVolunteer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True)
    can_do_central_checkin = models.BooleanField(default=False)


def __str__(self):
    return self.user.email


class EventCheckin(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    volunteer = models.ForeignKey(
        SrVolunteer, on_delete=models.SET_NULL, null=True, blank=True
    )


class FestCheckin(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    volunteer = models.ForeignKey(
        SrVolunteer, on_delete=models.SET_NULL, null=True, blank=True
    )
