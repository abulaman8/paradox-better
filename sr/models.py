from django.db import models
from django.contrib.auth.models import User
from core.models import Event


class SrVolunteer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True)
    can_do_central_checkin = models.BooleanField(default=False)
