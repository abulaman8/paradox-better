from django.db import models
from django.contrib.auth.models import User
from core.models import Department, SubDepartment, ApprovalStatus, Event


class ResourceCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class UnitOfMeasure(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    category = models.ForeignKey(
        ResourceCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="resources")
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure, on_delete=models.SET_NULL, null=True, blank=True, related_name="resources")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Requirement(models.Model):

    sources = (
        ("fr_arranged", "fr_arranged"),
        ("self_arranged", "self_arranged")
    )

    id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(
        Resource, on_delete=models.PROTECT, null=True, blank=True, related_name="requirements")

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="requirements")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True, related_name="requirements")
    sub_department = models.ForeignKey(
        SubDepartment, on_delete=models.CASCADE, null=True, blank=True, related_name="requirements")
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              null=True, blank=True, related_name="requirements")
    quantity = models.FloatField()
    description = models.TextField(null=True, blank=True)
    approval_status = models.ForeignKey(
        ApprovalStatus, on_delete=models.PROTECT)
    arrangement_source = models.CharField(
        choices=sources, null=True, blank=True, max_length=64)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.resource.name} - {self.quantity} - {self.author.username}"


class ReqAction(models.Model):
    id = models.AutoField(primary_key=True)
    requirement = models.ForeignKey(
        Requirement, on_delete=models.CASCADE, related_name='actions', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approval_status = models.ForeignKey(
        ApprovalStatus, on_delete=models.PROTECT)
