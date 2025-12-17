from django.db import transaction
from payments.models import Payment
from orders.models import Order
from webhooks.models import WebhookEvent

def process_payment_webhook(data):
    event_id = data["transaction_id"]

    if WebhookEvent.objects.filter(event_id=event_id).exists():
        return

    with transaction.atomic():
        WebhookEvent.objects.create(
            event_id=event_id,
            payload=data
        )

        payment = Payment.objects.select_for_update().get(
            transaction_id=data["transaction_id"]
        )

        order = Order.objects.select_for_update().get(
            id=data["order_id"]
        )

        if data["event"] == "PAYMENT_SUCCESS":
            payment.status = Payment.Status.SUCCESS
            order.status = Order.Status.PAID

        elif data["event"] == "PAYMENT_FAILED":
            payment.status = Payment.Status.FAILED
            order.status = Order.Status.FAILED

        payment.save()
        order.save()
