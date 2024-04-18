from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from emp.models import RegData
from forms.types import FormType, ElementType
from typing import List


class Command(BaseCommand):

    help = 'add element id to reg data\'s data field'

    def handle(self, *args, **options):
        regs = RegData.objects.all()
        # me = Student.objects.get(email='21f1000506@ds.study.iitm.ac.in')
        # regs = RegData.objects.filter(student=me).all()
        count = 0
        for reg in regs:
            data = reg.data
            form = FormType.from_dict(reg.form)

            user_inputs: List[ElementType] = []
            final_data = {}
            user_blocks = form.blocks
            for blk in user_blocks:
                elements = blk.elements
                for el in elements:
                    user_inputs.append(el)
            for i, el in enumerate(user_inputs):
                vel = el.element
                it = el.inputType
                final_data[i] = {
                    'id': el.id,
                    'label': el.label,
                    'value': ','.join(
                        map(str, vel["values"]  # type: ignore
                            ))if it == 'checkbox' else vel["value"]  # type: ignore
                }
            if not data['0'].get('id'):
                reg.data = final_data
                reg.save()
            count += 1
            # self.stdout.write(self.style.SUCCESS(
            #     f'Processed {count} registrations'))
            print(f"{count}/{len(regs)} processed", end='\r', flush=True)
