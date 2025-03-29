from apps.orders.models import Order

import requests

PAYMENT_URL = 'https://panel.aqayepardakht.ir/api/v2/create'
VERIFY_URL = 'https://panel.aqayepardakht.ir/api/v2/verify'
AQAYE_PARDAKHT_PIN = 'sandbox'

class PaymentService:
    @staticmethod
    def pay_request(amount, obj):
        payload = {
            'pin': AQAYE_PARDAKHT_PIN,
            'amount': amount,
            'callback': f"http://127.0.0.1:8000/api/orders/payment/callback/?type={'order' if isinstance(obj, Order) else 'subscription'}",
        }
        print(payload, 'service payload')
        response = requests.post(PAYMENT_URL, json=payload)
        print(response, 'service response')
        data = response.json()
        print(data, 'service data')
        if data.get('status') == 'success':
            transid = data.get('transid')
            obj.transaction_id = transid
            obj.save()
            payment_url = f'https://panel.aqayepardakht.ir/startpay/sandbox/{data.get('transid')}'

            return {'order_id': obj.id, 'amount': amount, 'payment_url': payment_url}

    @staticmethod
    def order_pay_verify(obj, status_code, transid):
        if status_code == '1':
            payload = {
                'pin': AQAYE_PARDAKHT_PIN,
                'amount': obj.get_final_cost(),
                'transid': transid
            }
            response = requests.post(VERIFY_URL, json=payload)
            data = response.json()

            if data.get('status') == 'success':
                obj.paid = True
                obj.save()
                return {'message': 'Payment successful'}

    @staticmethod
    def subscription_pay_verify(subscription, status_code, transid):
        if status_code == '1':
            payload = {
                'pin': AQAYE_PARDAKHT_PIN,
                'amount': subscription.price,
                'transid': transid
            }
            response = requests.post(VERIFY_URL, json=payload)
            data = response.json()

            if data.get('status') == 'success':
                subscription.paid = True
                subscription.is_active = True
                subscription.save()
                return {'message': 'Payment successful'}