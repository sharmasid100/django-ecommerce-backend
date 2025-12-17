from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product


@transaction.atomic
def reduce_stock(product_id, quantity):
    product = Product.objects.select_for_update().get(id=product_id)

    if product.stock_quantity < quantity:
        raise ValidationError('Insufficient stock')

    product.stock_quantity -= quantity
    product.save()

