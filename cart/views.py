from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Product
from .models import CartItem
from .serializers import CartSerializer
from .utils import get_user_cart


class AddToCartView(APIView):
    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = Product.objects.get(id=product_id, is_active=True)

        if quantity > product.stock_quantity:
            return Response(
                {"error": "Requested quantity exceeds stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_user_cart(request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            new_quantity = item.quantity + quantity

            if new_quantity > product.stock_quantity:
                return Response(
                    {"error": "Requested quantity exceeds stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity = new_quantity
            item.save()

        return Response(CartSerializer(cart).data)
    


class UpdateCartItemView(APIView):
    def put(self, request, item_id):
        quantity = int(request.data.get("quantity"))

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item = CartItem.objects.get(id=item_id, cart__user=request.user)

        if quantity > item.product.stock_quantity:
            return Response(
                {"error": "Requested quantity exceeds stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = quantity
        item.save()

        return Response(CartSerializer(item.cart).data)


class RemoveCartItemView(APIView):
    def delete(self, request, item_id):
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart = item.cart
        item.delete()

        return Response(CartSerializer(cart).data)

class CartDetailView(APIView):
    def get(self, request):
        cart = get_user_cart(request.user)
        return Response(CartSerializer(cart).data)
