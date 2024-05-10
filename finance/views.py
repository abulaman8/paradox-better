from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import status
from core.models import ApprovalStatus, Department, Event
from frb.models import Requirement
from utils.decorators import authed, has_bill_perms, has_budget_perms, has_perms, has_requirement_perms
from utils.fns import generate_voucher
from datetime import datetime
import json
from .models import Bill, DebitTransaction, CreditTransaction, Account, BankDetails, Vendor
from .serializers import BillSerializer, CreditTransactionSerializer, DebitTransactionSerializer
from frb.serializers import RequirementSerializer


@api_view(['GET'])
@has_perms(['view_account'])
def get_balance(request):
    data = request.GET
    id = data.get('dept_id')
    event_id = data.get('event_id')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            account = event.account
            debits = DebitTransaction.objects.filter(account=account).all()
            credits = CreditTransaction.objects.filter(account=account).all()
            net = sum([debit.amount for debit in debits]) - \
                sum([credit.amount for credit in credits])
            return Response({'balance': net}, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif id:
        try:
            dept = Department.objects.get(id=id)
            account = dept.account
            debits = DebitTransaction.objects.filter(account=account).all()
            credits = CreditTransaction.objects.filter(account=account).all()
            net = sum([debit.amount for debit in debits]) - \
                sum([credit.amount for credit in credits])
            return Response({'balance': net}, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Provide a department id or event id.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@has_perms(['view_account'])
def get_transactions(request):
    data = request.GET
    id = data.get('dept_id')
    event_id = data.get('event_id')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            account = event.account
            debits = DebitTransaction.objects.filter(account=account).all()
            credits = CreditTransaction.objects.filter(account=account).all()
            debits_serialized = DebitTransactionSerializer(debits, many=True)
            credits_serialized = CreditTransactionSerializer(
                credits, many=True)
            net = sum([debit.amount for debit in debits]) - \
                sum([credit.amount for credit in credits])
            return Response({
                'balance': net,
                'debits': debits_serialized.data,
                'credits': credits_serialized.data
            }, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif id:
        try:
            dept = Department.objects.get(id=id)
            account = dept.account
            debits = DebitTransaction.objects.filter(account=account).all()
            credits = CreditTransaction.objects.filter(account=account).all()
            debits_serialized = DebitTransactionSerializer(debits, many=True)
            credits_serialized = CreditTransactionSerializer(
                credits, many=True)
            net = sum([debit.amount for debit in debits]) - \
                sum([credit.amount for credit in credits])
            return Response({
                'balance': net,
                'debits': debits_serialized.data,
                'credits': credits_serialized.data
            }, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Provide a department id or event id.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@has_perms(['view_account'])
def get_txn_by_type(request, txn_type):
    if txn_type not in ['credit', 'debit']:
        return Response({'message': 'Invalid transaction type'}, status=status.HTTP_400_BAD_REQUEST)
    data = request.GET
    id = data.get('dept_id')
    event_id = data.get('event_id')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            account = event.account
            if txn_type == 'credit':
                transactions = CreditTransaction.objects.filter(
                    account=account).all()
                serializer = CreditTransactionSerializer(
                    transactions, many=True)
            else:
                transactions = DebitTransaction.objects.filter(
                    account=account).all()
                serializer = DebitTransactionSerializer(
                    transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif id:
        try:
            dept = Department.objects.get(id=id)
            account = dept.account
            if txn_type == 'credit':
                transactions = CreditTransaction.objects.filter(
                    account=account).all()
                serializer = CreditTransactionSerializer(
                    transactions, many=True)
            else:
                transactions = DebitTransaction.objects.filter(
                    account=account).all()
                serializer = DebitTransactionSerializer(
                    transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Provide a department id or event id.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@has_perms(['view_account'])
def get_all_dept_accounts(request):
    depts = Department.objects.all()
    r = []
    for dept in depts:
        account = dept.account
        d = {}
        d['id'] = dept.id
        d['name'] = dept.name
        credit_txns = CreditTransaction.objects.filter(account=account).all()
        debit_txns = DebitTransaction.objects.filter(account=account).all()
        net = sum([debit.amount for debit in debit_txns]) - \
            sum([credit.amount for credit in credit_txns])
        d['balance'] = net
        r.append(d)
    return Response(r, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_budget_perms(['assign_dept_budget'])
def assign_dept_budget(request, id):
    data = request.data
    description = data.get('description')
    try:
        master_account = Account.objects.filter(is_master=True).first()
        if not master_account:
            return Response({'message': 'Master account not found'}, status=status.HTTP_404_NOT_FOUND)
        dept = Department.objects.get(id=id)
        data = request.data
        budget = data.get('budget')
        account = dept.account
        with transaction.atomic():
            CreditTransaction.objects.create(
                account=master_account, amount=budget, description=description, txn_type='budget_allocation')
            DebitTransaction.objects.create(
                account=account, amount=budget, description=description, txn_type='budget_allocation')
        debits = DebitTransaction.objects.filter(account=account).all()
        credits = CreditTransaction.objects.filter(account=account).all()
        net = sum([debit.amount for debit in debits]) - sum(
            [credit.amount for credit in credits])
        return Response({'message': 'Budget assigned', 'balance': net}, status=status.HTTP_200_OK)

    except Department.DoesNotExist:
        return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@has_budget_perms(['assign_event_budget'])
def assign_event_budget(request, event_id):
    data = request.data
    id = data.get('dept_id')
    description = data.get('description')
    try:
        event = Event.objects.get(id=event_id)
        dept = event.department
        if dept.id != id:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        budget = data.get('budget')
        dept_account = dept.account
        event_account = event.account
        dept_credits = CreditTransaction.objects.filter(
            account=dept_account).all()
        dept_debits = DebitTransaction.objects.filter(
            account=dept_account).all()
        dept_net = sum([debit.amount for debit in dept_debits]) - \
            sum([credit.amount for credit in dept_credits])
        if dept_net < budget:
            return Response({'message': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            CreditTransaction.objects.create(
                account=dept_account, amount=budget, description=description, txn_type='budget_allocation')
            DebitTransaction.objects.create(
                account=event_account, amount=budget, description=description, txn_type='budget_allocation')
        return Response({'message': 'Budget assigned'}, status=status.HTTP_200_OK)

    except Event.DoesNotExist:
        return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@has_budget_perms(['deassign_dept_budget'])
def deassign_dept_budget(request, id):
    data = request.data
    amount = data.get('amount')
    description = data.get('description')
    try:
        master_account = Account.objects.filter(is_master=True).first()
        if not master_account:
            return Response({'message': 'Master account not found'}, status=status.HTTP_404_NOT_FOUND)
        dept = Department.objects.get(id=id)
        account = dept.account
        debit_txns = DebitTransaction.objects.filter(account=account).all()
        credit_txns = CreditTransaction.objects.filter(account=account).all()
        net = sum([debit.amount for debit in debit_txns]) - \
            sum([credit.amount for credit in credit_txns])
        if net < amount:
            return Response({'message': 'Not enough funds to deassign'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            DebitTransaction.objects.create(
                account=master_account, amount=amount, description=description, txn_type='budget_deallocation')
            CreditTransaction.objects.create(
                account=account, amount=amount, description=description, txn_type='budget_deallocation')
        credit_txns = CreditTransaction.objects.filter(account=account).all()
        debit_txns = DebitTransaction.objects.filter(account=account).all()
        net = sum([debit.amount for debit in debit_txns]) - sum(
            [credit.amount for credit in credit_txns])
        return Response({'message': 'Budget deassigned', 'balance': net}, status=status.HTTP_200_OK)

    except Department.DoesNotExist:
        return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@has_budget_perms(['deassign_event_budget'])
def deassign_event_budget(request, event_id):
    data = request.data
    id = data.get('dept_id')
    description = data.get('description')
    amount = data.get('amount')
    try:
        event = Event.objects.get(id=event_id)
        dept = event.department
        if dept.id != id:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
        dept_account = dept.account
        event_account = event.account
        event_credits = CreditTransaction.objects.filter(
            account=event_account).all()
        event_debits = DebitTransaction.objects.filter(
            account=event_account).all()
        event_net = sum([debit.amount for debit in event_debits]) - \
            sum([credit.amount for credit in event_credits])
        if event_net < amount:
            return Response({'message': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            DebitTransaction.objects.create(
                account=dept_account, amount=amount, description=description, txn_type='budget_deallocation')
            CreditTransaction.objects.create(
                account=event_account, amount=amount, description=description, txn_type='budget_deallocation')
        return Response({'message': 'Budget deassigned'}, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@has_bill_perms(['view_bill'])
def get_all_bills(request):
    data = request.GET
    id = data.get('dept_id')
    event_id = data.get('event_id')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            account = event.account
            bills = Bill.objects.filter(account=account).all()
            serializer = BillSerializer(bills, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif id:
        try:
            dept = Department.objects.get(id=id)
            account = dept.account
            events = Event.objects.filter(department=dept)
            event_accounts = [
                event.account for event in events.all()] if events.exists() else []
            event_bills = Bill.objects.filter(account__in=event_accounts).all()
            bills = Bill.objects.filter(
                account=account).all().union(event_bills)
            serializer = BillSerializer(bills, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'message': 'Department does not exist'})
    bill = Bill.objects.all()
    serializer = BillSerializer(bill, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@has_bill_perms(['view_bill'])
def get_bill(request, bill_id):
    data = request.GET
    id = data.get('dept_id')
    event_id = data.get('event_id')
    try:
        bill = Bill.objects.prefetch_related(
            'author',
            'account',
            'approval_status',
            'vendor',
            'vendor__bank_details',
        ).get(id=bill_id)
        serializer = BillSerializer(bill)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Bill.DoesNotExist:
        return Response({'message': 'Bill does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authed()
def get_my_bills(request):
    user = request.user
    bills = Bill.objects.filter(author=user).all()
    serializer = BillSerializer(bills, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@has_bill_perms(['add_bill'])
def upload_bill(request):
    data = request.data
    id = data.get('dept_id')
    event_id = data.get('event_id')
    # print(data)
    title = data.get('title')
    bill_type = data.get('bill_type')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)

            account = event.account
        except Event.DoesNotExist:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
    elif id:
        try:
            dept = Department.objects.get(id=id)
            account = dept.account
        except Department.DoesNotExist:
            return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Provide a department id or event id.'}, status=status.HTTP_400_BAD_REQUEST)
    amount = data.get('amount')
    requirement_ids = data.get('requirement_ids').split(',')
    description = data.get('description')
    pending = ApprovalStatus.objects.get(name='pending')
    file = request.FILES.get('file')
    # file = data.get('file')
    bill_number = data.get('bill_number')

    bill_date = datetime.fromisoformat(data.get('bill_date'))
    if not title or not bill_type or not amount or not requirement_ids or not file:
        return Response({
            'message': 'Title, bill_type, amount, requirement_ids and file are required'
        }, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        requirements = [Requirement.objects.get(id=requirement_id)
                        for requirement_id in requirement_ids]
        for requirement in requirements:
            if requirement.approval_status.name != 'final_level_approved':
                return Response({
                    'message': 'Requirement not approved by fr core'
                }, status=status.HTTP_400_BAD_REQUEST
                )
    except Requirement.DoesNotExist:
        return Response({
            'message': 'Requirement not found'
        }, status=status.HTTP_404_NOT_FOUND
        )
    if bill_type == 'vendor_full_payment' or bill_type == 'vendor_advance_payment':
        vendor = data.get('vendor')
        vendor = json.loads(vendor)
        vendor_bank_details = data.get('vendor_bank_details')
        vendor_bank_details = json.loads(vendor_bank_details)
        if not vendor or not vendor_bank_details:
            return Response({
                'message': 'Vendor details are required'
            }, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            if BankDetails.objects.filter(account_number=vendor_bank_details["account_number"]).exists():
                bank_details = BankDetails.objects.get(
                    account_number=vendor_bank_details["account_number"])
            else:
                bank_details = BankDetails.objects.create(
                    account_number=vendor_bank_details["account_number"],
                    ifsc_code=vendor_bank_details["ifsc_code"],
                    bank_name=vendor_bank_details["bank_name"],
                    branch_name=vendor_bank_details["branch_name"],
                    account_holder_name=vendor_bank_details["account_holder_name"]
                )
            if Vendor.objects.filter(gst_number=vendor["gst_number"]).exists():
                vendor_object = Vendor.objects.get(
                    gst_number=vendor["gst_number"])
            else:
                vendor_object = Vendor.objects.create(
                    name=vendor["name"], gst_number=vendor["gst_number"], bank_details=bank_details, address=vendor["address"])
            # vendor_object = Vendor.objects.get_or_create()

            new_bill = Bill.objects.create(
                author=request.user,
                title=title,
                bill_type=bill_type,
                amount=amount,
                account=account,
                total_amount=data.get(
                    'total_amount') if bill_type == 'vendor_advance_payment' else amount,
                description=description,
                approval_status=pending,
                file=file,
                vendor=vendor_object,
                bill_number=bill_number,
                bill_date=bill_date

            )
            new_bill.requirements.add(*requirements)
            new_bill.save()
            serializer = BillSerializer(new_bill)

            return Response({
                'message': 'Bill uploaded successfully',
                'bill': serializer.data
            }, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({
                'message': f'Bill not uploaded {e}'
            }, status=status.HTTP_404_NOT_FOUND
            )
    else:
        vendor = data.get('vendor')
        student_details = data.get('student_details')
        student_details = json.loads(student_details)
        upi = student_details.get('upi')
        phone = student_details.get('phone')
        if not upi or not phone:
            return Response({
                'message': 'UPI and phone number are required'
            }, status=status.HTTP_400_BAD_REQUEST
            )
        vendor = json.loads(vendor)
        if not vendor:
            return Response({
                'message': 'Vendor details are required'
            }, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            if Vendor.objects.filter(gst_number=vendor["gst_number"]).exists():
                vendor_object = Vendor.objects.get(
                    gst_number=vendor["gst_number"])
            else:
                vendor_object = Vendor.objects.create(
                    name=vendor["name"], gst_number=vendor["gst_number"], address=vendor["address"])
            new_bill = Bill.objects.create(
                author=request.user,
                title=title,
                bill_type=bill_type,
                amount=amount,
                upi=upi,
                phone=phone,
                account=account,
                description=description,
                approval_status=pending,
                file=file,
                bill_number=bill_number,
                bill_date=bill_date,
                vendor=vendor_object
            )
            new_bill.requirements.add(*requirements)
            new_bill.save()
            serializer = BillSerializer(new_bill)
            return Response({
                'message': 'Bill uploaded successfully',
                'bill': serializer.data
            }, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'message': f'Bill not uploaded {e}'
            }, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['PUT'])
@has_bill_perms(['first_level_bill_approval'])
def first_level_approval(request, bill_id):
    data = request.data
    try:
        bill = Bill.objects.get(id=bill_id)
        bill.approval_status = ApprovalStatus.objects.get(
            name='first_level_approved')
        bill.save()
        try:
            from_email = f"Finance & Requirements <{settings.EMAIL_HOST_USER}>"
            to = bill.author.email
            subject = "Bill approved"
            text_content = f"Dear {bill.author.username},\n\nYour bill {bill.title} with bill number {bill.bill_number} has been approved at the first level, and is pending one more level of approval. The same will be reflected on the finance portal.\n\n Regards,\n Finance and requirements."
            mail = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            mail.send()
        except Exception as e:
            print(e)
        serializer = BillSerializer(bill)
        return Response({
            'message': 'Bill approved successfully',
            'bill': serializer.data
        }, status=status.HTTP_200_OK
        )
    except Bill.DoesNotExist:
        return Response({
            'message': 'Bill does not exist'
        }, status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_bill_perms(['final_level_bill_approval'])
def final_level_approval(request, bill_id):
    data = request.data
    try:
        with transaction.atomic():
            bill = Bill.objects.select_for_update().get(id=bill_id)
            if bill.approval_status.name == 'final_level_approved':
                return Response({
                    "message": "Bill already approved"
                }, status=status.HTTP_400_BAD_REQUEST)
            bill.approval_status = ApprovalStatus.objects.get(
                name='final_level_approved')
            bill.save()
            account = bill.account
            dept = Department.objects.filter(account=account).first()
            event = Event.objects.filter(department=dept).first()
            if event:
                dept = event.department if event else None
            dept_account = dept.account if dept else None
            cred = CreditTransaction.objects.create(
                account=dept_account,
                amount=bill.amount,
                description=bill.description,
                txn_type='bill_payment',
                bill=bill
            )
        try:
            from_email = f"Finance & Requirements <{settings.EMAIL_HOST_USER}>"
            to = bill.author.email
            subject = "Bill approved"
            text_content = f"Dear {bill.author.username},\n\nYour bill {bill.title} with bill number {bill.bill_number} has been approved at the final level. The same will be reflected on the finance portal.\n\n Regards,\n Finance and requirements."
            mail = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            mail.send()
        except Exception as e:
            print(e)
        try:
            generate_voucher(bill.id)
        except Exception as e:
            print(e)
            serializer = BillSerializer(bill)
            return Response({
                'message': 'Bill approved successfully, but voucher not generated',
                'bill': serializer.data
            }, status=status.HTTP_200_OK)
        serializer = BillSerializer(bill)
        return Response({
            'message': 'Bill approved successfully',
            'bill': serializer.data
        }, status=status.HTTP_200_OK
        )
    except Bill.DoesNotExist:
        return Response({
            'message': 'Bill does not exist'
        }, status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_bill_perms(['first_level_bill_rejection'])
def first_level_rejection(request, bill_id):
    data = request.data
    message = data.get('message')
    if not message:
        return Response({
            'message': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        bill = Bill.objects.get(id=bill_id)
        bill.approval_status = ApprovalStatus.objects.get(
            name='first_level_rejected')
        bill.save()
        try:
            from_email = f"Finance & Requirements <{settings.EMAIL_HOST_USER}>"
            to = bill.author.email
            subject = "Bill rejected"
            text_content = f"Dear {bill.author.username},\n\nYour bill {bill.title} with bill number {bill.bill_number} has been rejected at the first level for the following reason\n\n {message}.\n\n. You can reupload a new bill The same will be reflected on the finance portal.\n\n Regards,\n Finance and requirements."

        except Exception as e:
            print(e)
        serializer = BillSerializer(bill)
        return Response({
            'message': 'Bill rejected successfully',
            'bill': serializer.data
        }, status=status.HTTP_200_OK
        )
    except Bill.DoesNotExist:
        return Response({
            'message': 'Bill does not exist'
        }, status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@has_bill_perms(['final_level_bill_rejection'])
def final_level_rejection(request, bill_id):
    data = request.data
    message = data.get('message')
    if not message:
        return Response({
            'message': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        bill = Bill.objects.get(id=bill_id)
        bill.approval_status = ApprovalStatus.objects.get(
            name='final_level_rejected')
        bill.save()
        serializer = BillSerializer(bill)
        return Response({
            'message': 'Bill rejected successfully',
            'bill': serializer.data
        }, status=status.HTTP_200_OK
        )
    except Bill.DoesNotExist:
        return Response({
            'message': 'Bill does not exist'
        }, status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@has_requirement_perms(['view_requirement'])
def get_all_approved_requirements(request):
    data = request.GET
    dept_id = data.get('dept_id')
    event_id = data.get('event_id')
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            requirements = Requirement.objects.filter(
                approval_status=ApprovalStatus.objects.get(name='final_level_approved')).filter(event=event).all()
            serialized = RequirementSerializer(requirements, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'message': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if dept_id:
        try:
            dept = Department.objects.get(id=dept_id)
            requirements = Requirement.objects.filter(
                approval_status=ApprovalStatus.objects.get(name='final_level_approved')).filter(department=dept).all()
            serialized = RequirementSerializer(requirements, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'message': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)
    requirements = Requirement.objects.filter(
        approval_status=ApprovalStatus.objects.get(name='final_level_approved')).all()
    serialized = RequirementSerializer(requirements, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def gen_dummy_vouch(request):
    generate_voucher(10)
    return Response({'message': 'dummy voucher generated'})
