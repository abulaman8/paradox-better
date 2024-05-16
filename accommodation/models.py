from django.contrib.auth.models import User
from django.db import models
from core.models import Student


class Supply(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class OTP(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    supplies = models.ManyToManyField(Supply, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.student.email} - {self.otp}"


class Hostel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Mess(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    floor = models.PositiveIntegerField(null=True, blank=True)
    caterer = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name + " - " + self.caterer


class Accommadation(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, null=True, blank=True)
    mess = models.ForeignKey(
        Mess, on_delete=models.CASCADE, null=True, blank=True)
    room = models.PositiveIntegerField(null=True, blank=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    supplies_given = models.ManyToManyField(
        Supply, blank=True, related_name='supplies_given')
    supplies_returned = models.ManyToManyField(
        Supply, blank=True, related_name='supplies_returned')
    supplies_checked_out = models.BooleanField(default=False)

    def __str__(self):
        return self.student.email + " - " + self.hostel.name + " - " + self.mess.name


class AccomVolunteer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hostels = models.ManyToManyField(Hostel, blank=True)

    def __str__(self):
        return self.user.email
