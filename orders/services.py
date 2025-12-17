from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from cart.models import Cart, CartItem
from products.models import Product
from .models import Order, OrderItem


class OrderStateError(Exception):
    pass


@transaction.atomic
def create_order_from_cart(user):
    """
    Converts user's cart into an order.

    Flow:
    Cart -> Order(PAYMENT_PENDING)
    - Validates stock
    - Snapshots product price & name
    - Deducts inventory
    - Clears cart
    """

    try:
        cart = Cart.objects.select_for_update().get(user=user)
    except ObjectDoesNotExist:
        raise OrderStateError("Cart does not exist")

    cart_items = (
        CartItem.objects
        .select_related("product")
        .filter(cart=cart)
    )

    if not cart_items.exists():
        raise OrderStateError("Cart is empty")

    total_amount = 0

    for item in cart_items:
        product = item.product

        if item.quantity > product.stock_quantity:
            raise OrderStateError(
                f"Insufficient stock for {product.name}"
            )

        total_amount += product.price * item.quantity

    order = Order.objects.create(
        user=user,
        status=Order.STATUS_PAYMENT_PENDING,
        total_amount=total_amount
    )

    for item in cart_items:
        product = item.product

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=item.quantity
        )

        product.stock_quantity -= item.quantity
        product.save()

    cart_items.delete()

    return order


@transaction.atomic
def mark_order_paid(order_id):
    """
    Called ONLY by payments app after successful payment.
    """

    order = Order.objects.select_for_update().get(id=order_id)

    if order.status != Order.STATUS_PAYMENT_PENDING:
        raise OrderStateError("Order cannot be marked as PAID")

    order.status = Order.STATUS_PAID
    order.save()

    return order


@transaction.atomic
def mark_order_failed(order_id):
    """
    Called ONLY by payments app after failed payment.
    """

    order = Order.objects.select_for_update().get(id=order_id)

    if order.status != Order.STATUS_PAYMENT_PENDING:
        raise OrderStateError("Order cannot be marked as FAILED")

    order.status = Order.STATUS_FAILED
    order.save()

    return order


@transaction.atomic
def cancel_order(order_id, user):
    """
    User-initiated cancellation.
    Allowed only before shipping.
    """

    order = Order.objects.select_for_update().get(id=order_id, user=user)

    if order.status in [Order.STATUS_SHIPPED, Order.STATUS_DELIVERED]:
        raise OrderStateError("Order cannot be cancelled")

    if order.status == Order.STATUS_CANCELLED:
        return order

    order.status = Order.STATUS_CANCELLED
    order.save()

    return order


@transaction.atomic
def ship_order(order_id):
    """
    Admin / system action.
    """

    order = Order.objects.select_for_update().get(id=order_id)

    if order.status != Order.STATUS_PAID:
        raise OrderStateError("Only paid orders can be shipped")

    order.status = Order.STATUS_SHIPPED
    order.save()

    return order


@transaction.atomic
def deliver_order(order_id):
    """
    Final lifecycle transition.
    """

    order = Order.objects.select_for_update().get(id=order_id)

    if order.status != Order.STATUS_SHIPPED:
        raise OrderStateError("Only shipped orders can be delivered")

    order.status = Order.STATUS_DELIVERED
    order.save()

    return order
