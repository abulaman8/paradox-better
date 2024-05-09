from django.core.management.base import BaseCommand
from finance.models import Bill, VoucherType, Voucher
from django.template import Context, Template
from utils.templates import voucher_template, paradox_new_logo, stact, sign, empty
from django.core.files.base import ContentFile
import uuid
import pdfkit


class Command(BaseCommand):

    help = 'get stats about registrations'

    def handle(self, *args, **options):
        bill_id = 10
        bill = Bill.objects.prefetch_related(
            'vendor',
            'vendor__bank_details',
        ).get(id=bill_id)
        bill_type = bill.bill_type
        voucher_type = VoucherType.objects.get(name=bill_type)
        img_data = "data:image/png;base64,"

        template = Template(voucher_template)
        data = {
            'voucher_number': f'VN-{bill_id}',
            'bill_number': bill.bill_number,
            'date': bill.bill_date.strftime('%d-%m-%Y'),
            'vendor': bill.vendor.name if bill.vendor else '',
            'dept': 'IT',
            'vendor_address': bill.vendor.address if bill.vendor else '',
            'gst_number': bill.vendor.gst_number if bill.vendor else '',
            'type': voucher_type.name,
            'total': bill.amount,
            'description': bill.description,
            'stact': f'{img_data}{stact}',
            'sign': f'{img_data}{sign}',
            'logo': f'{img_data}{paradox_new_logo}',
            'account_number': bill.vendor.bank_details.account_number if bill.vendor and bill.vendor.bank_details else '',
            'ifsc': bill.vendor.bank_details.ifsc_code if bill.vendor and bill.vendor.bank_details else '',
            'account_holder': bill.vendor.bank_details.account_holder_name if bill.vendor and bill.vendor.bank_details else '',
            'bank': bill.vendor.bank_details.bank_name if bill.vendor and bill.vendor.bank_details else '',
            'empty': f'{img_data}{empty}',

        }
        # print(data)
        context = Context(data)

        voucher = template.render(context)
        pdf_file = pdfkit.from_string(voucher)
        voucher = Voucher.objects.create(
            bill=bill,
            voucher_type=voucher_type,
        )
        voucher.file.save(f'{uuid.uuid4()}.pdf',
                          ContentFile(pdf_file), save=True)  # type: ignore
