from django.db import models
from core.models import Student


class Supply(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Hostel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Mess(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    floor = models.PositiveIntegerField()
    caterer = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " - " + self.caterer


class Accommadation(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    room = models.PositiveIntegerField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    supplies_given = models.ManyToManyField(Supply, blank=True)
    supplies_returned = models.ManyToManyField(Supply, blank=True)

    def __str__(self):
        return self.student.email + " - " + self.hostel.name + " - " + self.mess.name
