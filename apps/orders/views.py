from drf_spectacular.types import OpenApiTypes
from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .schema import ORDER_CREATE_ERROR_EXAMPLES

from .serializers import *

from .selectors.order_selectors import get_all_orders, filter_orders_by_user
from .selectors.subscription_selectors import get_all_subscription, filter_subscription_by_user

from .services.payment_services import *

class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = get_all_orders()

    @extend_schema(
        summary='List orders',
        description='Retrieve the list of orders for a user.',
        responses={200: OrderSerializer(many=True)},
    )
    def list(self, request):
        orders = filter_orders_by_user(request.user)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Create order',
        description='Create an order for a user.',
        request=OrderCreateSerializer,
        responses={
            201: OrderCreateSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Payment failed.',
                examples=ORDER_CREATE_ERROR_EXAMPLES
            )
        }
    )
    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        amount = order.get_total_cost()
        data = PaymentService.pay_request(amount, order)

        return Response(data, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = get_all_subscription()

    @extend_schema(
        summary='List subscriptions',
        description='Retrieve the list of subscriptions for a user.',
        responses={200: SubscriptionSerializer(many=True)},
    )
    def list(self, request):
        subscription = filter_subscription_by_user(request.user)
        serializer = SubscriptionSerializer(subscription, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Create subscription',
        description='Create a subscription for a user.',
        request=SubscriptionCreateSerializer,
        responses={
            201: SubscriptionCreateSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Payment failed.',
                examples=ORDER_CREATE_ERROR_EXAMPLES
            )
        }
    )
    def create(self, request):
        serializer = SubscriptionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        amount = subscription.price
        data = PaymentService.pay_request(amount, subscription)

        return Response(data, status=status.HTTP_201_CREATED)

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


