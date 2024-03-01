from django.contrib import admin
from .models import Account, Department, SubDepartment, ApprovalStatus, Role, Event, Student

admin.site.register(Account)
admin.site.register(Department)
admin.site.register(SubDepartment)
admin.site.register(ApprovalStatus)
admin.site.register(Role)
admin.site.register(Event)
admin.site.register(Student)
