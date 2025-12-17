from django.test import TransactionTestCase
from django.db import transaction
from orders.models import Order
from products.models import Product

class OrderAtomicityTest(TransactionTestCase):

    def test_order_rolls_back_on_inventory_failure(self):
        product = Product.objects.create(
            name="Laptop",
            price=50000,
            stock_quantity=0
        )

        with self.assertRaises(Exception):
            with transaction.atomic():
                # simulate order creation
                product.stock_quantity -= 1
                product.save()

        self.assertEqual(Order.objects.count(), 0)
