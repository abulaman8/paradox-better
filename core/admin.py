from django.contrib import admin
from .models import Account, Department, SubDepartment, ApprovalStatus, Role, Event, Student, Link, OTP, FAQ, QrCode, Sponsor, Blacklist, GalleryImage, Action

admin.site.register(Account)
admin.site.register(Department)
admin.site.register(SubDepartment)
admin.site.register(ApprovalStatus)
admin.site.register(Role)
admin.site.register(Event)
admin.site.register(Student)
admin.site.register(Link)
admin.site.register(OTP)
admin.site.register(FAQ)
admin.site.register(QrCode)
admin.site.register(Sponsor)
admin.site.register(Blacklist)
admin.site.register(GalleryImage)
admin.site.register(Action)
