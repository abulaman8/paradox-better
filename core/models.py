from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from forms.models import Form


class Blacklist(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Student(models.Model):
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    id = models.AutoField(primary_key=True)
    email = models.EmailField(null=True, blank=True)
    whatsapp = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    state = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    gender = models.CharField(
        max_length=8, choices=gender_choices, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        user = User.objects.get(email=self.email)
        return user.first_name + ' ' + user.last_name


class QrCode(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=256, unique=True)
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name='qr_code')
    image = models.ImageField(upload_to='qr_codes', null=True, blank=True)


class OTP(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    is_master = models.BooleanField(default=False)

    def __str__(self):
        return "Master" if self.is_master else f"slave no. {self.id}"


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    core = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='core_departments')
    members = models.ManyToManyField(
        User, related_name='member_departments', blank=True)
    account = models.OneToOneField(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='department')
    event_based = models.BooleanField(default=False)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='events')
    head = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='head_events')
    members = models.ManyToManyField(
        User, related_name='member_events', blank=True)
    account = models.OneToOneField(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='event')
    permissions = models.ManyToManyField(Permission, blank=True)
    is_approved = models.BooleanField(default=False)
    open = models.BooleanField(default=True)
    max_participants = models.IntegerField(null=True, blank=True)
    is_team_event = models.BooleanField(default=False)
    max_team_size = models.IntegerField(null=True, blank=True)
    min_team_size = models.IntegerField(null=True, blank=True)
    header_image = models.ImageField(
        upload_to='event_header_images', null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_start_date = models.DateTimeField(null=True, blank=True)
    registration_end_date = models.DateTimeField(null=True, blank=True)
    fee = models.IntegerField(default=0)
    location = models.CharField(max_length=360, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    form = models.ForeignKey(
        Form, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class SubDepartment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    team_lead = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='head_sub_departments')
    members = models.ManyToManyField(
        User, related_name='member_sub_departments', blank=True)
    account = models.OneToOneField(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_department')
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    users = models.ManyToManyField(User, related_name='roles', blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.name} - {str(self.content_object)}'


class Link(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    url = models.URLField()

    def __str__(self):
        return self.name + "-" + str(self.content_object)


class Sponsor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='sponsors')
    url = models.URLField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name + " - " + self.title + " - " + str(self.content_object)


class GalleryImage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to='gallery')

    def __str__(self):
        return self.name + " - " + str(self.content_object)


class FAQ(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=100)
    answer = models.TextField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.content_object) + " - " + self.question


class ApprovalStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_student(sender, instance, created, **kwargs):
    if created:
        Student.objects.get_or_create(email=instance.email)


@receiver(post_save, sender=Department)
def create_department_account(sender, instance, created, **kwargs):
    if created:
        account = Account.objects.create()
        instance.account = account
        dept_default_perm_codes = ["view_requirement", "add_requirement"]
        dept_default_perms = Permission.objects.filter(
            codename__in=dept_default_perm_codes).all()
        role_names = ["deputy core", "core", "super coordinator",
                      "coordinator", "volunteer", "ground volunteer"]
        for role_name in role_names:
            role = Role.objects.create(
                name=role_name,
                content_type=ContentType.objects.get_for_model(Department),
                object_id=instance.id
            )
        core_role = Role.objects.get(name="core", content_type=ContentType.objects.get_for_model(
            Department), object_id=instance.id)
        core_role.users.add(instance.core)
        core_req_perm_codes = [
            "first_level_req_approval",
            "first_level_req_rejection",
            "change_role",
            "view_role",
            "manage_member",
            "view_account",
            "add_event",
            "change_event",
            "delete_event",
            "add_round",
            "change_round",
            "delete_round",
            "approve_event",
        ]
        core_req_perms = Permission.objects.filter(
            codename__in=core_req_perm_codes).all()
        core_role.permissions.add(*core_req_perms)
        core_role.save()
        print("before setting permissions")
        print(dept_default_perms)
        instance.permissions.set(dept_default_perms)
        instance.save()
        print("after setting permissions")
        print(instance.permissions.all())


@receiver(post_save, sender=SubDepartment)
def create_sub_department_account(sender, instance, created, **kwargs):
    if created:
        account = Account.objects.create()
        instance.account = account
        team_lead = instance.team_lead
        role_type = ContentType.objects.get(
            app_label='frb',
            model='role'
        )
        req_codenames = ["view_requirement", "add_requirement"]
        permissions = Permission.objects.filter(
            codename__in=req_codenames).all()
        instance.permissions.add(*permissions)
        instance.save()
        role_names = ["team_lead"]
        for role_name in role_names:
            role = Role.objects.create(
                name=role_name,
                content_type=ContentType.objects.get_for_model(SubDepartment),
                object_id=instance.id
            )
        team_lead_role = Role.objects.get(
            name="team_lead", content_object=instance)
        team_lead_role.users.add(team_lead)
        team_lead_perm_codes = ["change_role", "view_role", "manage_member"]
        team_lead_perms = Permission.objects.filter(
            codename__in=team_lead_perm_codes).all()
        team_lead_role.permissions.add(*team_lead_perms)
        team_lead_role.save()


@receiver(post_save, sender=Event)
def create_event_account(sender, instance, created, **kwargs):
    if created:
        account = Account.objects.create()
        instance.account = account

        head = instance.head
        req_codenames = ["view_requirement", "add_requirement"]
        permissions = Permission.objects.filter(
            codename__in=req_codenames).all()
        instance.permissions.add(*permissions)
        instance.save()
        role_names = ["head", "super coordinator", "coordinator", "volunteer"]
        for role_name in role_names:
            role = Role.objects.create(
                name=role_name,
                content_type=ContentType.objects.get_for_model(Event),
                object_id=instance.id
            )
        head_role = Role.objects.get(
            name="head", content_type=ContentType.objects.get_for_model(Event), object_id=instance.id)
        head_role.users.add(head)
        head_perm_codes = ["change_role", "view_role", "manage_member"]
        head_perms = Permission.objects.filter(
            codename__in=head_perm_codes).all()
        head_role.permissions.add(*head_perms)
        head_role.save()


@receiver(pre_delete, sender=Department)
def delete_department_handler(sender, instance, **kwargs):
    dept_type = ContentType.objects.get_for_model(Department)
    instance.account.delete()
    roles = Role.objects.filter(
        content_type=dept_type, object_id=instance.id).delete()
