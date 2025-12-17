from django.urls import path
from .views import (
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    CartDetailView
)

urlpatterns = [
    path("", CartDetailView.as_view()),
    path("add/", AddToCartView.as_view()),
    path("item/<int:item_id>/update/", UpdateCartItemView.as_view()),
    path("item/<int:item_id>/remove/", RemoveCartItemView.as_view()),
]
