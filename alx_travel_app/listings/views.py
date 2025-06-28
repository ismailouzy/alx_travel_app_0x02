import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Payment

@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    url = 'https://api.chapa.co/v1/transaction/initialize'

    payload = {
        "amount": data['amount'],
        "currency": "ETB",
        "email": data['email'],
        "first_name": data.get('first_name', 'Anonymous'),
        "last_name": data.get('last_name', 'User'),
        "tx_ref": data['booking_reference'],
        "callback_url": "http://localhost:8000/api/verify-payment/",  # update if needed
        "return_url": "http://localhost:8000/payment-success/",
        "customization": {
            "title": "Booking Payment",
            "description": "Payment for travel booking"
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)
    res_data = response.json()

    if res_data.get('status') == 'success':
        payment = Payment.objects.create(
            booking_reference=data['booking_reference'],
            amount=data['amount'],
            transaction_id=res_data['data']['tx_ref'],
            status='Pending'
        )
        return Response({"payment_url": res_data['data']['checkout_url']})
    return Response({"error": res_data}, status=400)


@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.query_params.get('tx_ref')
    url = f'https://api.chapa.co/v1/transaction/verify/{tx_ref}'
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    res_data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
    except Payment.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)

    if res_data.get('status') == 'success' and res_data['data']['status'] == 'success':
        payment.status = 'Completed'
    else:
        payment.status = 'Failed'
    payment.save()
    return Response({"status": payment.status})


