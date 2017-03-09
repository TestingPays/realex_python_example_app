import unittest
from django.test import Client
import requests
from lxml import html


class RealexAuthIntegrationTests(unittest.TestCase):
    def test_main_index_page_returns_status_code_200(self):
        self.assertEqual(Client().get('/').status_code, 200)

    def test_create_charge_of_success_with_http_status_code_of_200(self):
        response = _invoke_post_request('250.00')
        self.assertEqual(200, response.status_code)
        self.assertEqual('SUCCESS', response.json()['message'])
        self.assertEqual('00', response.json()['realex_result_code'])

    def test_create_transaction_declined_offline_with_status_code_of_200(self):
        response = _invoke_post_request('250.11')
        self.assertEqual(200, response.status_code)
        self.assertEqual('DECLINED', response.json()['message'])
        self.assertEqual('107', response.json()['realex_result_code'])

    def test_create_fraud_checks_blocked_transaction_with_status_code_of_200(self):
        response = _invoke_post_request('250.13')
        self.assertEqual(200, response.status_code)
        self.assertEqual('DECLINED', response.json()['message'])
        self.assertEqual('107', response.json()['realex_result_code'])

    def test_create_cvv_not_processed_status_code_of_200(self):
        response = _invoke_post_request('250.33')
        self.assertEqual(200, response.status_code)
        self.assertEqual('DECLINED', response.json()['message'])
        self.assertEqual('107', response.json()['realex_result_code'])

    def test_create_auth_request_timeout(self):
        response = _invoke_post_request('250.60')
        self.assertEqual(200, response.status_code)
        self.assertEqual('timeout', response.json()['message'])


def _invoke_post_request(amount):
    return Client().post('/auth', data=_generate_data(amount),
                         content_type='application/x-www-form-urlencoded; charset=UTF-8')


class Realex3DSecureIntegrationTests(unittest.TestCase):
    """Verify Enrolled"""

    def test_3d_secure_verify_enrollment_card_holder_not_enrolled_failed(self):
        response = _invoke_three_d_secure('250.20')
        self.assertEqual(200, response.status_code)
        self.assertEqual('Not Enrolled', response.json()['message'])
        self.assertEqual('110', response.json()['realex_result_code'])

    def test_3d_secure_verify_enrollment_message_timeout_failed(self):
        response = _invoke_three_d_secure('250.21')
        self.assertEqual(200, response.status_code)
        self.assertEqual('Unable to verify enrollment', response.json()['message'])
        self.assertEqual('220', response.json()['realex_result_code'])

    def test_3d_secure_verify_enrollment_currency_mismatch_failed(self):
        response = _invoke_three_d_secure('250.22')
        self.assertEqual(200, response.status_code)
        self.assertEqual('Currency Mismatch', response.json()['message'])
        self.assertEqual('507', response.json()['realex_result_code'])

    def test_3d_secure_verify_enrollment_card_expired_failed(self):
        response = _invoke_three_d_secure('250.23')
        self.assertEqual(200, response.status_code)
        self.assertEqual('Invalid Expiry Date', response.json()['message'])
        self.assertEqual('509', response.json()['realex_result_code'])

    def test_3d_secure_verify_enrollment_invalid_cardholder_name_failed(self):
        response = _invoke_three_d_secure('250.24')
        self.assertEqual(200, response.status_code)
        self.assertEqual('Invalid Card Name', response.json()['message'])
        self.assertEqual('502', response.json()['realex_result_code'])

    """Verify 3ds Signed"""

    def test_create_3d_secure_verify_signed_verification_unavailable_with_eci_0(self):
        response = _invoke_three_d_secure('250.07')
        self.assertEqual(200, response.status_code)

        response = _invoke_third_party_redirect(response)
        self.assertEqual(302, response.status_code)

        response = _invoke_callback(response)
        self.assertEqual(200, response.status_code)

        self.assertEqual('Verification unavailable', _parse_response_message(response))
        self.assertEqual('00', _parse_response_realex_result_code(response))
        self.assertEqual('U', _parse_response_status(response))
        self.assertEqual('0', _parse_response_eci(response))

    def test_create_3d_secure_verify_signed_verification_failed_with_eci_1(self):
        response = _invoke_three_d_secure('250.09')
        self.assertEqual(200, response.status_code)

        response = _invoke_third_party_redirect(response)
        self.assertEqual(302, response.status_code)

        response = _invoke_callback(response)
        self.assertEqual(200, response.status_code)

        self.assertEqual('Verification Failed', _parse_response_message(response))
        self.assertEqual('110', _parse_response_realex_result_code(response))
        self.assertEqual('A', _parse_response_status(response))
        self.assertEqual('1', _parse_response_eci(response))

    def test_create_3d_secure_verify_signed_verification_failed_with_eci_7(self):
        response = _invoke_three_d_secure('250.10')
        self.assertEqual(200, response.status_code)

        response = _invoke_third_party_redirect(response)
        self.assertEqual(302, response.status_code)

        response = _invoke_callback(response)
        self.assertEqual(200, response.status_code)

        self.assertEqual('Verification Failed', _parse_response_message(response))
        self.assertEqual('110', _parse_response_realex_result_code(response))
        self.assertEqual('N', _parse_response_status(response))
        self.assertEqual('7', _parse_response_eci(response))

    """Verify Auth"""

    def test_create_3d_secure_charge_of_success(self):
        response = _invoke_three_d_secure('250.00')
        self.assertEqual(200, response.status_code)

        response = _invoke_third_party_redirect(response)
        self.assertEqual(302, response.status_code)

        response = _invoke_callback(response)
        self.assertEqual(200, response.status_code)

        self.assertEqual('SUCCESS', _parse_response_message(response))
        self.assertEqual('00', _parse_response_realex_result_code(response))

    def test_create_3d_secure_auth_bank_communication_error(self):
        response = _invoke_three_d_secure('250.01')
        self.assertEqual(200, response.status_code)

        response = _invoke_third_party_redirect(response)
        self.assertEqual(302, response.status_code)

        response = _invoke_callback(response)
        self.assertEqual(200, response.status_code)

        self.assertEqual('BANK_ERROR', _parse_response_message(response))
        self.assertEqual('200', _parse_response_realex_result_code(response))

    def test_create_3d_secure_auth_fraudulent(self):
        response = _invoke_three_d_secure('250.13')
        self.assertEqual(200, response.status_code)

        response = _invoke_third_party_redirect(response)
        self.assertEqual(302, response.status_code)

        response = _invoke_callback(response)
        self.assertEqual(200, response.status_code)

        self.assertEqual('Verification Failed', _parse_response_message(response))
        self.assertEqual('110', _parse_response_realex_result_code(response))


def _invoke_three_d_secure(amount):
    return Client().post('/threedsecure', data=_generate_data(amount),
                         content_type='application/x-www-form-urlencoded; charset=UTF-8')


def _invoke_third_party_redirect(response):
    return requests.post(
        _parse_url(response),
        data=_parse_response_data(response),
        allow_redirects=False,
        headers={'Content-Type': 'application/json'})


def _invoke_callback(response):
    return Client().get(response.headers['Location'])


def _parse_response_message(response):
    return _parse_response(response, 'message')


def _parse_response_realex_result_code(response):
    return _parse_response(response, 'realex_result_code')


def _parse_response_status(response):
    return _parse_response(response, 'status')


def _parse_response_eci(response):
    return _parse_response(response, 'eci')


def _parse_response(response, item):
    return response.context[3].dicts[3][item]


def _parse_url(response):
    return html.fromstring(response.content).xpath('//form[@id="accept-form"]')[0].action


def _parse_response_data(response):
    return {'ApiKey': html.fromstring(response.content).xpath('//input[@name="ApiKey"]')[0].value,
            'RequestId': html.fromstring(response.content).xpath('//input[@name="RequestId"]')[0].value,
            'MD': html.fromstring(response.content).xpath('//input[@name="MD"]')[0].value,
            'PaReq': html.fromstring(response.content).xpath('//input[@name="PaReq"]')[0].value,
            'termUrl': html.fromstring(response.content).xpath('//input[@name="termUrl"]')[0].value}


def _generate_data(amount):
    return "card_holder_name=John+Doe&amount=" + amount + \
           "&card_number=4111+1111+1111+1111&cvv=222&card_type=VISA&currency=EUR&expiry_month=12&expiry_year=23"
