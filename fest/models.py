from django.db import models
from core.models import Student


class FestRegistrstion(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    likelihood = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.student.email


class AccomodationRegistration(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True)
    arrival_date = models.DateTimeField(null=True, blank=True)
    departure_date = models.DateTimeField(null=True, blank=True)
    jain_food = models.BooleanField(default=False)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact_name = models.CharField(
        max_length=256, null=True, blank=True)
    emergency_contact_relation = models.CharField(
        max_length=256, null=True, blank=True)
    medical_issues = models.TextField(null=True, blank=True)
    pwd = models.BooleanField(default=False)
    pwd_certificate = models.FileField(
        upload_to='pwd_certificates/', null=True, blank=True)
    outside_india = models.BooleanField(default=False)
    passport = models.FileField(upload_to='passport/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return self.student.email
