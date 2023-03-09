from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import User,Account,Transaction
from .forms import UserForm, MyUserCreationForm,PaymentForm,TransferForm
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt    
import json
from decimal import Decimal
from django.conf import settings
import requests
import retrying
import uuid
from django.db import transaction
from django.core import serializers


@login_required
def transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            # Set the recipient's bank account details from the form data
            account_number = form.cleaned_data['account_number']
            bank_code = form.cleaned_data['bank_code']
            account_name = form.cleaned_data['account_name']

            # Set the transfer details from the form data
            amount = form.cleaned_data['amount']  # Amount in kobo (i.e. 5000 Naira)
            reason = form.cleaned_data['reason']

            # Set the Paystack secret key
            secret_key = 'sk_test_faa54d269889aadb009588f2fae9aead0f0e901e'

            # Set the API endpoints
            recipient_url = 'https://api.paystack.co/transferrecipient'
            transfer_url = 'https://api.paystack.co/transfer'

            # Set the headers for the requests
            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }

            # Set the payload for creating the transfer recipient
            recipient_payload = {
                'type': 'nuban',
                'name': account_name,
                'account_number': account_number,
                'bank_code': bank_code,
                'currency': 'NGN'
            }

            # Send a POST request to the API endpoint to create the transfer recipient
            recipient_response = requests.post(recipient_url, headers=headers, json=recipient_payload)

            # If the request was successful, the response status code should be 201
            if recipient_response.status_code == 201:
                # Extract the recipient code from the JSON payload
                recipient_data = recipient_response.json()['data']
                recipient_code = recipient_data['recipient_code']
                print(f'The recipient with account number {account_number} and name {account_name} has been created with recipient code {recipient_code}')

                # Set the payload for initiating the transfer
                transfer_payload = {
                    'source': 'balance',
                    'amount': amount,
                    'recipient': recipient_code,
                    'reason': reason
                }

                # Send a POST request to the API endpoint to initiate the transfer
                transfer_response = requests.post(transfer_url, headers=headers, json=transfer_payload)

                # If the request was successful, the response status code should be 200
                if transfer_response.status_code == 200:
                    # Extract the transfer details from the JSON payload
                    transfer_data = transfer_response.json()['data']
                    transfer_amount = transfer_data['amount'] / 100 # Convert amount back to Naira
                    transfer_recipient = transfer_data['recipient']
                    transfer_status = transfer_data['status']
                    print(f'A transfer of {transfer_amount} Naira has been initiated to recipient {transfer_recipient} with status {transfer_status}')
                    return redirect('home')
                else:
                    # If the request was not successful, print out the error message
                    print(f'Error {transfer_response.status_code}: {transfer_response.json()["message"]}')
                    return render(request, 'error.html', {'message': transfer_response.json()["message"]})
            else:
                # If the request was not successful, print out the error message
                print(f'Error {recipient_response.status_code}: {recipient_response.json()["message"]}')
                return render(request, 'error.html', {'message': recipient_response.json()["message"]})
    else:
        form = TransferForm()
        context = {'form': form}
        return render(request, 'wallet/transfer.html',context)



#transaction id
def generate_transaction_number():
    # Generate a UUID and convert it to a decimal integer
    uuid_int = int(uuid.uuid4().hex, 16)

    # Take the last 10 digits of the integer and return as a string
    return str(uuid_int)[-10:]

# Set your Paystack API key
PAYSTACK_API_KEY = settings.PAYSTACK_API_KEY

# Set the API endpoint for funding a Paystack wallet
url = 'https://api.paystack.co/transaction/initialize'

# Set the request headers
headers = {
    'Authorization': f'Bearer {PAYSTACK_API_KEY}',
    'Content-Type': 'application/json'
}


@retrying.retry(wait_exponential_multiplier=5, wait_exponential_max=5)
def make_request(payload):
    # Send a POST request to the API endpoint with the headers and payload
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        # Return the authorization URL for the payment
        return data['data']['authorization_url']
    else:
        # Return the response from the API
        return f"Error {response.status_code}: {response.text}"


def banks(request):
    headers = {
        'Authorization': 'Bearer sk_test_faa54d269889aadb009588f2fae9aead0f0e901e',
        'Content-Type': 'application/json'
    }

    url = 'https://api.paystack.co/bank'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        banks = response.json()['data']
        bank_list = []
        for bank in banks:
            bank_dict = {
                'name': bank['name'],
                'code': bank['code']
            }
            bank_list.append(bank_dict)
        return JsonResponse({'data': bank_list})
    else:
        return JsonResponse({'error': response.text}, status=response.status_code)


@csrf_exempt
def paystackWebhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        if data['event'] == 'charge.success':
            transaction_data = data['data']
            sender_data = transaction_data['authorization']
            receiver_data = transaction_data['metadata']
            wallet_id = transaction_data['metadata']['wallet_id']
            transaction_amount = Decimal(transaction_data['amount'])
            recipient_account = Account.objects.get(account_number=wallet_id)
            recipient_account.account_balance=int(recipient_account.account_balance)+int(transaction_amount)
            recipient_account.save()
            transaction = Transaction.objects.create(
                transaction_channel=transaction_data['channel'],
                sender_account_name=sender_data.get('account_name', ''),
                sender_account_number=sender_data.get('last4', ''),
                sender_bank=sender_data.get('bank', ''),
                sender_email='',
                receiver_account_name=receiver_data.get('wallet_owner', ''),
                receiver_account_number=receiver_data.get('wallet_id', ''),
                receiver_bank='wallet',
                receiver_email=receiver_data.get('email', ''),
                transaction_status=transaction_data['status'],
                transaction_reference=transaction_data['reference'],
                transaction_amount=Decimal(transaction_data['amount']),
                transaction_description=transaction_data['gateway_response'],
                transaction_time=transaction_data['paid_at']
            )

            transaction.save()
            return redirect('dashboard')
    else:
        return redirect('login')


def home(request):
    return render(request, 'wallet/index.html')
def about(request):
    return render(request, 'wallet/about.html')



def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'An error occurred during registration. Please check the following errors: {}'.format(form.errors))
     
    return render(request, 'wallet/login_register.html', {'form': form})

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username **OR password does not exit')

    context = {'page': page}
    return render(request, 'wallet/login_register.html', context)


@login_required
def logoutUser(request):
    logout(request)
    return redirect('home')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    account = Account.objects.get(user=request.user)
    form = UserForm(instance=user)
    context = {'user': user,'form':form,'account':account}
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    return render(request, 'wallet/profile.html', context)
@login_required
def dashboard(request):
     user = None
     try:
        user = User.objects.get(id=request.user.id)
     except:
        messages.error(request, 'User does not exist')
     if user:        
        account = Account.objects.get(user=request.user)
        transactions = Transaction.objects.filter(Q(sender_account_number=account.account_number) | Q(receiver_account_number=account.account_number)).order_by('-transaction_time')[:5]
        context = {'user': user,'account':account,'transactions':transactions}
        return render(request, 'wallet/dashboard.html',context)
     else:
        return redirect('login')

@login_required
def transactions(request):
    try:
        user = User.objects.get(id=request.user.id)
    except:
        messages.error(request, 'User does not exist')
    if user:        
        account = Account.objects.get(user=request.user)
        transactions = Transaction.objects.filter(Q(sender_account_number=account.account_number) | Q(receiver_account_number=account.account_number)).order_by('-transaction_time')
        context = {'user': user,'account':account,'transactions':transactions}
        return render(request, 'wallet/transactions.html',context)
    else:
        return redirect('login')



@login_required
@transaction.atomic
def sendMoney(request):
    transaction_reference = generate_transaction_number()
    if request.method == 'POST':
        print(request.POST)
        try:
            transaction_reference = generate_transaction_number()
            sender_account = Account.objects.select_for_update().get(user=request.user)
            recipient_account = Account.objects.select_for_update().get(account_number=request.POST.get('accountnumber'))
            amount = int(request.POST.get('amount'))

        # Validate inputs and check if the sender has sufficient balance
            if amount <= 0:
                raise ValueError('Invalid amount')
            if sender_account.account_balance < amount:
                raise ValueError('Insufficient balance')

        # Perform the transaction
            sender_account.account_balance -= amount
            recipient_account.account_balance += amount
            sender_account.save()
            recipient_account.save()

        # Create the transaction record
            transaction = Transaction.objects.create(
            transaction_channel='wallet',
            sender_account_name=sender_account.user.name,
            sender_account_number=sender_account.account_number,
            sender_bank='wallet',
            sender_email='',
            receiver_account_name=recipient_account.user.name,
            receiver_account_number=recipient_account.account_number,
            receiver_bank='wallet',
            transaction_status='success',
            transaction_reference=transaction_reference,
            transaction_amount=amount
        )
            transaction.save()

            return redirect('dashboard')
        except Exception as e:
        # Roll back the transaction if an error occurs
            transaction.set_rollback(True)
            messages.error(request, str(e))
            return render(request, 'wallet/sendmoney.html')

    else:
        messages.error(request, 'An error occurred during registration.')
     
    return render(request, 'wallet/sendmoney.html')

def checkAccount(request):
    if request.method == 'GET' and request.is_ajax():
        account_number = request.GET.get('account_number', None)
        if account_number:
            account = get_object_or_404(Account, account_number=account_number)
            print(account)
            data = {
                'name': account.user.name,
                'balance': account.account_balance,
                'account_number': account.account_number,
                # Add any other relevant data here
            }
            return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'})

def search(request):
    if request.method == 'GET' and request.is_ajax():
        q = request.GET.get('q', '')

        search_results = Transaction.objects.filter(
            Q(transaction_type__icontains=q) |
            Q(transaction_channel__icontains=q) |
            Q(transaction_status__icontains=q) |
            Q(sender_account_name__icontains=q) |
            Q(sender_account_number__icontains=q) |
            Q(sender_bank__icontains=q) |
            Q(receiver_account_name__icontains=q) |
            Q(receiver_account_number__icontains=q) |
            Q(receiver_bank__icontains=q) |
            Q(transaction_reference__icontains=q) |
            Q(transaction_amount__icontains=q) |
            Q(transaction_description__icontains=q) |
            Q(transaction_time__icontains=q)
        )

        transactions_dict = serializers.serialize('python', search_results)
        transactions_list = [item['fields'] for item in transactions_dict]

        data = {'transactions': transactions_list}
        print(transactions_list)
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'})

@login_required
def fundWallet(request):
    if request.method == 'POST':
        # Create a PaymentForm instance with the POST data
        form = PaymentForm(request.POST)
        account = Account.objects.get(user=request.user)  
        amount = request.POST.get('amount')
        account_number = account.account_number
        account_name =account.user.name

            # Update the payload with the form data
        payload = {
            'email' :'oguntayohabeebullah@gmail.com',
   'amount': amount,
    'metadata': {
        
        'wallet_id': account_number,
        'wallet_owner': account_name,
        'description': 'Funding my Paystack wallet'
    }
}


            # Call the make_request function to send the request, with retries if it fails
        response = make_request(payload)

            # Redirect to the authorization URL for the payment
            
        return HttpResponseRedirect(response)
    else:
        # Render the form in the GET request
        form = PaymentForm()

    return render(request, 'wallet/fund_wallet.html', {'form': form})





