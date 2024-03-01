from django.contrib.auth.models import User
from django.db import models
from core.models import Account, ApprovalStatus
from frb.models import Requirement

# Create your models here.


class VoucherType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class BankDetails(models.Model):
    id = models.AutoField(primary_key=True)
    account_holder_name = models.CharField(max_length=32)
    bank_name = models.CharField(max_length=256)
    branch_name = models.CharField(max_length=256)
    account_number = models.CharField(max_length=32, unique=True)
    ifsc_code = models.CharField(max_length=32)

    def __str__(self):
        return self.account_holder_name


class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    gst_number = models.CharField(max_length=32, unique=True)
    address = models.TextField(null=True, blank=True)
    bank_details = models.OneToOneField(
        BankDetails, on_delete=models.PROTECT, related_name="vendor", null=True, blank=True)

    def __str__(self):
        return self.name


class Bill(models.Model):

    bill_type_choices = [
        ('vendor_full_payment', 'vendor_full_payment'),
        ('student_reimbursement', 'student_reimbursement'),
        ('vendor_advance_payment', 'vendor_advance_payment'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="bills", null=True, blank=True)
    bill_number = models.CharField(max_length=32, unique=True)
    bill_date = models.DateField()

    file = models.FileField(upload_to="bills/", null=True, blank=True)
    account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="bills")
    requirements = models.ManyToManyField(Requirement, related_name="bills")
    amount = models.FloatField()
    description = models.TextField()
    approval_status = models.ForeignKey(
        ApprovalStatus, on_delete=models.PROTECT)
    bill_type = models.CharField(
        max_length=32, choices=bill_type_choices, default='vendor_payment')
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, related_name="bills", null=True, blank=True)
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Voucher(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    voucher_type = models.ForeignKey(VoucherType, on_delete=models.PROTECT)
    file = models.FileField(upload_to="vouchers/", null=True, blank=True)
    bill = models.OneToOneField(
        Bill, null=True, blank=True, on_delete=models.PROTECT, related_name="voucher")

    def __str__(self):
        return f"{self.bill} - {self.voucher_type}"


txn_type_choices = [
    ('budget_allocation', 'budget_allocation'),
    ('budget_deallocation', 'budget_deallocation'),
    ('bill_payment', 'bill_payment'),
    ('bill_reimbursement', 'bill_reimbursement'),
    ('bill_advance', 'bill_advance'),
]


class CreditTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.FloatField()
    txn_type = models.CharField(
        max_length=32, choices=txn_type_choices, default='bill_payment')
    description = models.TextField(null=True, blank=True)
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT,
                             related_name="credit_transactions", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.account)} - {self.amount}"


class DebitTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    txn_type = models.CharField(
        max_length=32, choices=txn_type_choices, default='budget_allocation')
    amount = models.FloatField()
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.account)} - {self.amount}"
