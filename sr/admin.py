from django.contrib import admin
from .models import SrVolunteer, FestCheckin, EventCheckin

admin.site.register(SrVolunteer)
admin.site.register(FestCheckin)
admin.site.register(EventCheckin)
