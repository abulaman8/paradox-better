from django.core.management.base import BaseCommand, CommandError
from core.models import Student
from accommodation.models import Accommadation, Mess, Hostel


class Command(BaseCommand):

    help = 'create accom entries from csv'

    def handle(self, *args, **options):
        with open('male.csv') as f:
            male = f.read().splitlines()
        with open('female.csv') as f:
            female = f.read().splitlines()
        full = male + female
        # full = ["319,Sharavathi,100,23F2004900,Aishetri Das,23-05-2024,02-06-2024,23f2004900@ds.study.iitm.ac.in",
        #         "320,Sharavathi,100,23F2004332,Dipakshi Kashyap,23-05-2024,02-06-2024,23f2004332@ds.study.iitm.ac.in",
        #         "321,Sharavathi,700,23F3000222,Nishat Bano,23-05-2024,02-06-2024,23f3000222@ds.study.iitm.ac.in",
        #         "322,Sharavathi,700,23F3000219,Pradeepa B,23-05-2024,02-06-2024,23f3000219@es.study.iitm.ac.in",
        #         "323,Sharavathi,900,22F3000653,Riya Agarwal,23-05-2024,02-06-2024,22f3000653@ds.study.iitm.ac.in",
        #         "324,Sharavathi,900,23F2005104,Yochana Vadlakonda,23-05-2024,02-06-2024,23f2005104@ds.study.iitm.ac.in"
        #         ]
        mess = Mess.objects.first()
        hostels = {}
        for h in Hostel.objects.all():
            hostels[h.name] = h
        accoms = []
        count = 0
        print(hostels)

        for f in full:
            spl = f.split(',')
            email = spl[7]
            hostel = spl[1]
            room = spl[2]
            hobj = hostels.get(hostel)
            if not hobj:
                print(f"{email} not allotted, {hostel} not found")
                count += 1
                continue
            accoms.append(Accommadation(
                student=Student.objects.get(email=email),
                room=room,
                mess=mess,
                hostel=hobj
            ))
            count += 1
            print(f"{count}/{len(full)} ready...", end='\r', flush=True)
        Accommadation.objects.bulk_create(accoms)

        print(accoms)
