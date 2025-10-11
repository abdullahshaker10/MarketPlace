"""
Payment Views - LSP Experimentation

Django views to demonstrate and experiment with Liskov Substitution Principle.
Users can test different payment processors through the web interface.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from decouple import config

from apps.payments.models import PaymentService
from apps.products.market_factories import get_marketplace_factory


class PaymentDemoView(View):
    def get(self, request):
        context = {
            "stripe_api_key": config("STRIPE_API_KEY", default="test"),
            "paypal_client_id": config("PAYPAL_CLIENT_ID", default="test"),
        }
        return render(request, "payments/demo.html", context)

    def post(self, request):
        try:
            market = request.POST.get("market", "US")
            amount = float(request.POST.get("amount", 0))
            payment_token = request.POST.get("payment_token", "demo_token")

            factory = get_marketplace_factory(market)

            payment_processor = factory.create_payment_processor()
            shipping_service = factory.create_shipping_service()
            tax_service = factory.create_tax_service()

            payment_service = PaymentService(payment_processor)
            payment_result = payment_service.charge_customer(amount, payment_token)

            tax = tax_service.calculate_tax(amount, "some_address")
            shipment = shipping_service.create_shipment("some_address", {})

            return JsonResponse(
                {
                    "success": payment_result.success,
                    "market": market,
                    "processor": payment_result.processor_name,
                    "transaction_id": payment_result.transaction_id,
                    "amount": payment_result.amount,
                    "tax": tax,
                    "shipment": shipment,
                    "error_message": payment_result.error_message,
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                    "lsp_message": "❌ Error occurred during processing",
                }
            )


@csrf_exempt
def api_payment(request):
    """
    API endpoint for payment processing
    """
    pass


def compare_processors(request):
    """
    View that demonstrates LSP by running the same payment through both processors
    """
    if request.method == "POST":
        try:
            amount = float(request.POST.get("amount", 50.00))
            payment_token = request.POST.get("payment_token", "compare_token")

            # Process with both processors using the SAME code
            stripe_processor = StripeProcessor("sk_test_stripe")
            paypal_processor = PayPalProcessor("paypal_client", "paypal_secret")

            # Same PaymentService code works with both! (LSP compliance)
            stripe_service = PaymentService(stripe_processor)
            paypal_service = PaymentService(paypal_processor)

            stripe_result = stripe_service.charge_customer(amount, payment_token)
            paypal_result = paypal_service.charge_customer(amount, payment_token)

            return JsonResponse(
                {
                    "lsp_demonstration": "Same code processed payments through both processors!",
                    "stripe_result": {
                        "success": stripe_result.success,
                        "processor": stripe_result.processor_name,
                        "transaction_id": stripe_result.transaction_id,
                        "amount": stripe_result.amount,
                    },
                    "paypal_result": {
                        "success": paypal_result.success,
                        "processor": paypal_result.processor_name,
                        "transaction_id": paypal_result.transaction_id,
                        "amount": paypal_result.amount,
                    },
                    "lsp_success": "Both processors were substitutable without code changes!",
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "POST method required"}, status=405)


def _get_processor(processor_type: str):
    """
    Factory function to create processors

    This function demonstrates how easy it is to add new processors
    without breaking existing code (Open-Closed Principle too!)
    """
    if processor_type == "stripe":
        return StripeProcessor("sk_test_stripe_demo")
    elif processor_type == "paypal":
        return PayPalProcessor("paypal_demo_client", "paypal_demo_secret")
    else:
        raise ValueError(f"Unknown processor type: {processor_type}")


def lsp_explanation(request):
    """
    View that explains LSP with the payment processor example
    """
    context = {
        "principle": "Liskov Substitution Principle",
        "definition": "Objects of a superclass should be replaceable with objects of a subclass without breaking the application.",
        "payment_example": {
            "interface": "PaymentProcessor",
            "implementations": ["StripeProcessor", "PayPalProcessor"],
            "method": "process_payment(amount, token) -> PaymentResult",
            "benefit": "Same PaymentService code works with both processors",
        },
        "violations_prevented": [
            "Different method names (charge_card vs process_payment)",
            "Different parameters (card_token vs paypal_token)",
            "Different return types (dict vs object)",
            "Different error handling approaches",
        ],
    }

    return render(request, "payments/lsp_explanation.html", context)
