from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from core.models import Student
from fest.models import FestRegistrstion
from fest.views import fest_reg_template
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class Command(BaseCommand):

    help = 'send mail to all registered users for fest.'

    def handle(self, *args, **options):
        regs = FestRegistrstion.objects.all()
        # email = '21f3002911@ds.study.iitm.ac.in'
        # user = User.objects.get(email=email)
        # student = Student.objects.get(user=user)
        # from_email = settings.EMAIL_HOST_USER
        # headers = {'Reply-To': "support@iitmparadox.org"}
        # template = Template(fest_reg_template)
        # context = Context({
        #     'student_name': student.user.last_name if student.user.first_name[0] == '2' else student.user.first_name + ' ' + student.user.last_name,
        # })
        # subject = "Get Ready for Paradox'24 - Exciting Updates Await!"
        # from_email = settings.EMAIL_HOST_USER
        # to = student.user.email
        # rendered = template.render(context)
        # email = EmailMultiAlternatives(
        #     subject, rendered, from_email, [to], headers=headers)
        # email.attach_alternative(rendered, "text/html")
        # try:
        #     email.send()
        #     self.stdout.write(self.style.SUCCESS(
        #         'Successfully sent mail to "%s"' % student.user.email))
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(
        #         'Failed to send mail to "%s" because "%s"' % (student.user.email, e)))
        for reg in regs:
            with open('mail.log', 'a') as f:
                student = reg.student
                from_email = settings.EMAIL_HOST_USER
                headers = {'Reply-To': "support@iitmparadox.org"}
                template = Template(fest_reg_template)
                context = Context({
                    'student_name': student.user.last_name if student.user.first_name[0] == '2' else student.user.first_name + ' ' + student.user.last_name,
                })
                subject = "Get Ready for Paradox'24 - Exciting Updates Await!"
                from_email = settings.EMAIL_HOST_USER
                to = student.user.email
                rendered = template.render(context)
                email = EmailMultiAlternatives(
                    subject, rendered, from_email, [to], headers=headers)
                email.attach_alternative(rendered, "text/html")
                try:
                    email.send()
                    f.write('Successfully sent mail to "%s"\n' %
                            student.user.email)
                    self.stdout.write(self.style.SUCCESS(
                        'Successfully sent mail to "%s"' % student.user.email))
                except Exception as e:
                    f.write('Failed to send mail to "%s" because "%s"\n' %
                            (student.user.email, e))
                    self.stdout.write(self.style.ERROR(
                        'Failed to send mail to "%s" because "%s"' % (student.user.email, e)))
                    continue
