from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from payments.services import initiate_payment

class PaymentInitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        force_status = request.data.get("status")

        payment = initiate_payment(order, force_status)

        return Response({
            "order_id": order.id,
            "payment_status": payment.status,
            "transaction_id": payment.transaction_id
        })
