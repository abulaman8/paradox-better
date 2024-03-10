from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.serializers import ApprovalStatusSerializer, DepartmentSerializer, SimpleUserSerializer, SubDepartmentSerializer
from .models import Resource, ResourceCategory, Requirement, UnitOfMeasure, ReqAction


class UnitOfMeasureSerializer(ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'


class ResourceCategorySerializer(ModelSerializer):
    class Meta:
        model = ResourceCategory
        fields = '__all__'


class ResourceSerializer(ModelSerializer):
    category = ResourceCategorySerializer()
    unit_of_measure = UnitOfMeasureSerializer()

    class Meta:
        model = Resource
        fields = '__all__'


class ReqActionSerializer(ModelSerializer):
    approval_status = ApprovalStatusSerializer()
    user = SimpleUserSerializer()

    class Meta:
        model = ReqAction
        exclude = ["requirement"]


class RequirementSerializer(ModelSerializer):
    resource = ResourceSerializer()
    approval_status = ApprovalStatusSerializer()
    author = SimpleUserSerializer()
    department = DepartmentSerializer()
    sub_department = SubDepartmentSerializer()
    all_messages = SerializerMethodField()

    class Meta:
        model = Requirement
        # fields = '__all__'
        fields = ['id', 'resource', 'author', 'department', 'sub_department', 'event', 'quantity',
                  'description', 'approval_status', 'arrangement_source', 'message', 'created_at', 'updated_at', 'all_messages']

    def get_all_messages(self, obj):
        return ReqActionSerializer(obj.actions.all(), many=True).data
