from django.urls import path
from webhooks.views import PaymentWebhookView

urlpatterns = [
    path("payment/", PaymentWebhookView.as_view())
]
