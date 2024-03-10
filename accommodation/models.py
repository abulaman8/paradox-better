from django.db import models
from core.models import Student


class Accommadation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.PositiveIntegerField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    supplies_given = models.BooleanField(default=False)
    supplies_returned = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
