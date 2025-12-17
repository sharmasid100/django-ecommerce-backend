import uuid
import random
from django.db import transaction
from payments.models import Payment
from orders.models import Order

@transaction.atomic
def initiate_payment(order: Order, force_status=None):
    """
    force_status can be:
    - "SUCCESS"
    - "FAILED"
    - None (random)
    """

    if order.status != Order.STATUS_PAYMENT_PENDING:
        raise ValueError("Order not eligible for payment")

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount
    )

    # MOCK DECISION
    if force_status:
        payment_success = force_status == Payment.STATUS_SUCCESS
    else:
        payment_success = random.choice([True, False])

    if payment_success:
        payment.status = Payment.STATUS_SUCCESS
        payment.transaction_id = str(uuid.uuid4())

        order.status = Order.STATUS_PAID
        order.save()

    else:
        payment.status = Payment.STATUS_FAILED
        order.status = Order.STATUS_FAILED
        order.save()

    payment.save()
    return payment
