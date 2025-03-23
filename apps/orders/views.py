import requests
from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *


PAYMENT_URL = 'https://panel.aqayepardakht.ir/api/v2/create'
VERIFY_URL = 'https://panel.aqayepardakht.ir/api/v2/verify'
AQAYE_PARDAKHT_PIN = 'sandbox'


class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        amount = order.get_final_cost()

        payload = {
            'pin': AQAYE_PARDAKHT_PIN,
            'amount': amount,
            'callback': 'http://127.0.0.1:8000/api/payment/callback/',
        }
        response = requests.post(PAYMENT_URL, json=payload)
        data = response.json()

        if data.get('status') == 'success':
            transid = data.get('transid')
            order.transaction_id = transid
            order.save()
            payment_url = f'https://panel.aqayepardakht.ir/startpay/sandbox/{data.get('transid')}'
            return Response(
                {'order_id': order.id, 'amount': amount, 'payment_url': payment_url},
                status=status.HTTP_201_CREATED,
            )

        return Response({'error': 'Failed to initiate payment'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(views.APIView):
    def post(self, request):
        transid = request.data.get('transid')
        status_code = request.data.get('status')
        try:
            order = Order.objects.get(transaction_id=transid)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if status_code == '1':
            payload = {
                'pin': AQAYE_PARDAKHT_PIN,
                'amount': order.get_final_cost(),
                'transid': transid
            }
            response = requests.post(VERIFY_URL, json=payload)
            data = response.json()

            if data.get('status') == 'success':
                order.paid = True
                order.save()
                return Response({'message': 'Payment successful'})

        return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)