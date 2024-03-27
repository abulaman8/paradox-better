from django.contrib import admin
from .models import Form, Input, CheckboxGroup, Select, RadioGroup, Block, Dependency


admin.site.register(Form)
admin.site.register(Input)
admin.site.register(CheckboxGroup)
admin.site.register(Select)
admin.site.register(RadioGroup)
admin.site.register(Block)
admin.site.register(Dependency)
