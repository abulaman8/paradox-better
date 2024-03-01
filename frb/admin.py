from django.contrib import admin
from .models import Resource, ResourceCategory, Requirement, UnitOfMeasure

admin.site.register(Resource)
admin.site.register(ResourceCategory)
admin.site.register(Requirement)
admin.site.register(UnitOfMeasure)
