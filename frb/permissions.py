from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Requirement

req_type = ContentType.objects.get_for_model(Requirement)
req_type.
permission = Permission.objects.create(
    codename='can_view_department_requirements',
    name='Can view department requirements',
    content_type=req_type
)
