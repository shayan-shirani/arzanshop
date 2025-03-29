from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .serializers import *

from .selectors.subscription_selectors import get_all_subscription

from .services.payment_services import *


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
        data = PaymentService.pay_request(amount, order)

        if data:
            return Response(data, status=status.HTTP_201_CREATED)

        return Response({'error': 'Failed to initiate payment'}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionBuyView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    queryset = get_all_subscription()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        amount = subscription.price
        data = PaymentService.pay_request(amount, subscription)

        if data:
            return Response(data, status=status.HTTP_201_CREATED)

        return Response({'error': 'Failed to initiate payment'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(views.APIView):
    def post(self, request):
        transid = request.data.get('transid')
        status_code = request.data.get('status')
        order_type = request.query_params.get('type')

        if order_type == 'order':
            try:
                order = Order.objects.get(transaction_id=transid)
                data = PaymentService.order_pay_verify(order, status_code, transid)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        elif order_type == 'subscription':
            try:
                subscription = Subscription.objects.get(transaction_id=transid)
                data = PaymentService.subscription_pay_verify(subscription, status_code, transid)
            except Subscription.DoesNotExist:
                return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'error': 'Invalid payment type'}, status=status.HTTP_400_BAD_REQUEST)

        if data:
            return Response(data, status=status.HTTP_200_OK)

        return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)


