from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Bill, BankDetails, Vendor, Voucher, VoucherType, DebitTransaction, CreditTransaction
from core.serializers import ApprovalStatusSerializer
from frb.serializers import RequirementSerializer


class VoucherTypeSerializer(ModelSerializer):
    class Meta:
        model = VoucherType
        fields = '__all__'


class BankDetailsSerializer(ModelSerializer):
    class Meta:
        model = BankDetails
        fields = '__all__'


class VendorSerializer(ModelSerializer):
    bank_details = BankDetailsSerializer(read_only=True)

    class Meta:
        model = Vendor
        fields = '__all__'


class BillSerializer(ModelSerializer):
    approval_status = ApprovalStatusSerializer(read_only=True)
    requirements = RequirementSerializer(read_only=True, many=True)
    department = SerializerMethodField()
    sub_department = SerializerMethodField()
    event = SerializerMethodField()
    bill_date = SerializerMethodField()
    user_details = SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['id', 'title', 'bill_number', 'bill_date', 'file', 'requirements', 'amount', 'total_amount', 'description',
                  'approval_status', 'bill_type', 'vendor', 'date_created', 'message', 'department', 'sub_department', 'event', 'user_details']
        read_only_fields = ['id', 'title', 'bill_number', 'bill_date', 'file', 'requirements', 'amount', 'total_amount', 'description',
                            'approval_status', 'bill_type', 'vendor', 'date_created', 'message', 'department', 'sub_department', 'event', 'user_details']

    def get_bill_date(self, obj):
        return obj.bill_date.strftime('%Y-%m-%d')

    def get_department(self, obj):
        try:
            return obj.account.department.name
        except:
            return None

    def get_sub_department(self, obj):
        try:
            return obj.account.sub_department.name
        except:
            return None

    def get_event(self, obj):
        try:
            return obj.account.event.name
        except:
            return None

    def get_user_details(self, obj):
        return {
            "name": obj.author.first_name + " " + obj.author.last_name,
            "email": obj.author.email,
            "upi": obj.upi,
            "phone": obj.phone

        }


class VoucherSerializer(ModelSerializer):
    voucher_type = VoucherTypeSerializer()
    bill = BillSerializer(read_only=True)

    class Meta:
        model = Voucher
        fields = '__all__'


class DebitTransactionSerializer(ModelSerializer):
    department = SerializerMethodField()
    sub_department = SerializerMethodField()
    event = SerializerMethodField()

    class Meta:
        model = DebitTransaction
        fields = ['id', 'amount', 'txn_type', 'description', 'date_created',
                  'department', 'sub_department', 'event']
        read_only_fields = ['id', 'amount', 'txn_type', 'description', 'date_created',
                            'department', 'sub_department', 'event']

    def get_department(self, obj):
        try:
            return obj.account.department.name
        except:
            return None

    def get_sub_department(self, obj):
        try:
            return obj.account.sub_department.name
        except:
            return None

    def get_event(self, obj):
        try:
            return obj.account.event.name
        except:
            return None


class CreditTransactionSerializer(ModelSerializer):
    bill = SerializerMethodField()
    department = SerializerMethodField()
    sub_department = SerializerMethodField()
    event = SerializerMethodField()

    class Meta:
        model = CreditTransaction
        fields = ['id', 'amount', 'txn_type', 'description', 'bill', 'date_created',
                  'department', 'sub_department', 'event']
        read_only_fields = ['id', 'bill', 'txn_type', 'description', 'amount',
                            'date_created', 'department', 'sub_department', 'event']

    def get_bill(self, obj):
        try:
            return obj.bill.bill_number
        except:
            return None

    def get_department(self, obj):
        try:
            return obj.account.department.name
        except:
            return None

    def get_sub_department(self, obj):
        try:
            return obj.account.sub_department.name
        except:
            return None

    def get_event(self, obj):
        try:
            return obj.account.event.name
        except:
            return None
