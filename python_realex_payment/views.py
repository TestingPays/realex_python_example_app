from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import HttpResponse
from realex.realex import Realex
import base64
import json

Realex.SHARED_SECRET = settings.REALEX_SHARED_SECRET
Realex.AUTH_URL = settings.REALEX_URL
Realex.MERCHANT_ID = settings.REALEX_MERCHANT_ID
Realex.VERIFY_SIGNED_URL = settings.REALEX_VERIFY_SIGNED_URL
Realex.VERIFY_ENROLLED_URL = settings.REALEX_VERIFY_ENROLLED_URL
Realex.CALLBACK_URL = settings.REALEX_CALLBACK_URL


@require_http_methods(['GET'])
def main(request):
    return render(request, "index.html")


@require_http_methods(['POST'])
def auth(request):
    response = Realex.create_charge(
        amount=request.POST['amount'],
        currency=request.POST['currency'],
        card_holder_name=request.POST['card_holder_name'],
        card_number=request.POST['card_number'],
        cvv=request.POST['cvv'],
        expiry_month=request.POST['expiry_month'],
        expiry_year=request.POST['expiry_year'],
        card_type=request.POST['card_type']
    )
    return HttpResponse(json.dumps(response), content_type="application/json")


@require_http_methods(['POST'])
def three_d_secure(request):
    request_body = request.body
    response = Realex.verify_enrolled(amount=request.POST['amount'],
                                      currency=request.POST['currency'],
                                      card_holder_name=request.POST['card_holder_name'],
                                      card_number=request.POST['card_number'],
                                      expiry_month=request.POST['expiry_month'],
                                      expiry_year=request.POST['expiry_year'],
                                      card_type=request.POST['card_type'])

    if response['enrolled'] == 'Y':
        response = Realex.redirect_to_secure_site(third_party_url=response['url'],
                                                  pareq=response['pareq'],
                                                  merchant_data=_encrypt_and_encode_merchant_data(request_body,
                                                                                                  response),
                                                  request_id='tp_python_realex_example')
        return HttpResponse(response.text)
    else:
        return HttpResponse(json.dumps(response), content_type="application/json")


def _encrypt_and_encode_merchant_data(request_body, response):
    return base64.b64encode(_encrypt_merchant_data(_extract_merchant_data(request_body, response)))


def _encrypt_merchant_data(merchant_data):
    # TODO: apply encryption to merchant data prior to encoding
    return merchant_data


def _extract_merchant_data(request_body, response):
    return str.encode(str(bytes.decode(request_body) + '&' + 'order_id=' + response['order_id'] + '&' + 'sha1hash=' + response['sha1hash']))


@require_http_methods(['GET'])
def three_ds_verify_signed(request):
    pa_res = request.GET.get('PaRes', '')
    merchant_data = _decrypt_and_decode_merchant_data(request.GET.get('MD', ''))

    response = Realex.verify_signed(amount=merchant_data['amount'],
                                    currency=merchant_data['currency'],
                                    pares=pa_res,
                                    sha1hash=merchant_data['sha1hash'],
                                    order_id=merchant_data['order_id'])

    if response['realex_result_code'] == '00' and (response['status'] == 'Y' or response['status'] == 'A'):
        response = Realex.create_charge(
            amount=merchant_data['amount'],
            currency=merchant_data['currency'],
            card_holder_name=merchant_data['card_holder_name'],
            card_number=merchant_data['card_number'],
            cvv=merchant_data['cvv'],
            expiry_month=merchant_data['expiry_month'],
            expiry_year=merchant_data['expiry_year'],
            card_type=merchant_data['card_type'],
            cavv=response['cavv'],
            xid=response['xid'],
            eci=response['eci']
        )
        return render(request, "index.html", response)

    return render(request, "index.html", response)


def _decrypt_and_decode_merchant_data(merchant_data):
    payment_details_dict = {}
    decoded_merchant_data = _decode_string(merchant_data)
    decrypted_merchant_data = _decrypt_merchant_data(decoded_merchant_data)
    for item in decrypted_merchant_data.split('&'):
        payment_details_dict[item[:item.find('=')]] = item[item.find('=') + 1:].replace('+', ' ')

    return payment_details_dict


def _decrypt_merchant_data(merchant_data):
    # TODO: apply decryption to merchant data after decoding
    return merchant_data


def _decode_string(string):
    return base64.b64decode(string).decode('utf-8')
