from django.db import models
from core.models import Student


class FestRegistrstion(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    likelihood = models.CharField(max_length=256)

    def __str__(self):
        return self.student.email


class AccomodationRegistration(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    jain_food = models.BooleanField(default=False)
    emergency_contact = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=256)
    emergency_contact_relation = models.CharField(max_length=256)
    medical_issues = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.student.email
