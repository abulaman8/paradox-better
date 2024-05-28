from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile, File
from core.models import Student, QrCode
import uuid
from utils.fns import generate_qr_code


class Command(BaseCommand):

    help = 'generate qr'

    def handle(self, *args, **options):
        # with open('accom_qr.txt', 'r') as f:
        #     emails = f.read().splitlines()
        emails = ['22f1000598@ds.study.iitm.ac.in']
        count = 0
        students = Student.objects.filter(email__in=emails)
        for student in students:
            code = uuid.uuid4()
            img = generate_qr_code(code)
            img.save('qr.png')
            with open('qr.png', 'rb') as f:
                image = File(f, name='qr.png')
                try:
                    qr_code = QrCode.objects.create(
                        code=code,
                        student=student,
                        image=image
                    )
                except:
                    pass

                count += 1
            print(f"{count}/{len(emails)} qrs generated", end='\r', flush=True)
