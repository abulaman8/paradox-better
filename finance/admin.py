from django.contrib import admin
from .models import Vendor, Voucher, Bill, VoucherType, BankDetails, DebitTransaction, CreditTransaction, Split

admin.site.register(Vendor)
admin.site.register(Voucher)
admin.site.register(Bill)
admin.site.register(VoucherType)
admin.site.register(BankDetails)
admin.site.register(DebitTransaction)
admin.site.register(CreditTransaction)
admin.site.register(Split)
