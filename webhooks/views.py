from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from webhooks.utils import verify_signature
from webhooks.services import process_payment_webhook

class PaymentWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        signature = data.get("signature")

        if not verify_signature(data, signature):
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        process_payment_webhook(data)

        return Response(
            {"status": "processed"},
            status=status.HTTP_200_OK
        )
