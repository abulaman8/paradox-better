from django.contrib import admin
from .models import Resource, ResourceCategory, Requirement, UnitOfMeasure, ReqAction

admin.site.register(Resource)
admin.site.register(ResourceCategory)
admin.site.register(Requirement)
admin.site.register(UnitOfMeasure)
admin.site.register(ReqAction)
