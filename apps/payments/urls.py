"""
Payment URLs for LSP demonstration
"""

from django.urls import path
from .views import PaymentDemoView, api_payment

urlpatterns = [
    path("demo/", PaymentDemoView.as_view(), name="payment_demo"),
    path("api/", api_payment, name="api_payment"),
]
