"""
Payment URLs for LSP demonstration
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_demo, name='demo'),
    path('api/', views.api_payment, name='api'),
    path('compare/', views.compare_processors, name='compare'),
    path('lsp-explanation/', views.lsp_explanation, name='explanation'),
]