from django.urls import path
from payments.views import PaymentInitAPIView

urlpatterns = [
    path("pay/<int:order_id>/", PaymentInitAPIView.as_view()),
]
