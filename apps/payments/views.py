"""
Payment Views - LSP Experimentation

Django views to demonstrate and experiment with Liskov Substitution Principle.
Users can test different payment processors through the web interface.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import PaymentService, StripeProcessor, PayPalProcessor


def payment_demo(request):
    """
    Main view to demonstrate LSP with payment processors
    
    Shows how the same code works with different processors
    """
    if request.method == 'GET':
        # Show the demo page
        context = {
            'processors': ['stripe', 'paypal'],
            'demo_amounts': [10.99, 25.50, 99.99, 199.99]
        }
        return render(request, 'payments/demo.html', context)
    
    elif request.method == 'POST':
        # Process payment using selected processor
        try:
            # Get form data
            processor_type = request.POST.get('processor')
            amount = float(request.POST.get('amount', 0))
            payment_token = request.POST.get('payment_token', 'demo_token')
            
            # Create the appropriate processor
            processor = _get_processor(processor_type)
            
            # Create payment service (same for both processors!)
            payment_service = PaymentService(processor)
            
            # Process payment (LSP in action - same code for both!)
            result = payment_service.charge_customer(amount, payment_token)
            
            return JsonResponse({
                'success': result.success,
                'processor': result.processor_name,
                'transaction_id': result.transaction_id,
                'amount': result.amount,
                'error_message': result.error_message,
                'lsp_message': f"✅ LSP Success! Same PaymentService code worked with {result.processor_name}"
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'lsp_message': "❌ Error occurred during processing"
            })


@csrf_exempt
def api_payment(request):
    """
    API endpoint to test LSP programmatically
    
    POST /payments/api/ with JSON:
    {
        "processor": "stripe" or "paypal",
        "amount": 99.99,
        "payment_token": "test_token"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            processor_type = data.get('processor')
            amount = float(data.get('amount', 0))
            payment_token = data.get('payment_token', 'api_token')
            
            # Demonstrate LSP - same code for both processors
            processor = _get_processor(processor_type)
            payment_service = PaymentService(processor)
            result = payment_service.charge_customer(amount, payment_token)
            
            return JsonResponse({
                'success': result.success,
                'processor_name': result.processor_name,
                'transaction_id': result.transaction_id,
                'amount': result.amount,
                'error_message': result.error_message,
                'lsp_demo': {
                    'message': 'This API works identically with both Stripe and PayPal!',
                    'principle': 'Liskov Substitution Principle',
                    'benefit': 'Processors are completely interchangeable'
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)


def compare_processors(request):
    """
    View that demonstrates LSP by running the same payment through both processors
    """
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 50.00))
            payment_token = request.POST.get('payment_token', 'compare_token')
            
            # Process with both processors using the SAME code
            stripe_processor = StripeProcessor('sk_test_stripe')
            paypal_processor = PayPalProcessor('paypal_client', 'paypal_secret')
            
            # Same PaymentService code works with both! (LSP compliance)
            stripe_service = PaymentService(stripe_processor)
            paypal_service = PaymentService(paypal_processor)
            
            stripe_result = stripe_service.charge_customer(amount, payment_token)
            paypal_result = paypal_service.charge_customer(amount, payment_token)
            
            return JsonResponse({
                'lsp_demonstration': 'Same code processed payments through both processors!',
                'stripe_result': {
                    'success': stripe_result.success,
                    'processor': stripe_result.processor_name,
                    'transaction_id': stripe_result.transaction_id,
                    'amount': stripe_result.amount
                },
                'paypal_result': {
                    'success': paypal_result.success,
                    'processor': paypal_result.processor_name,
                    'transaction_id': paypal_result.transaction_id,
                    'amount': paypal_result.amount
                },
                'lsp_success': 'Both processors were substitutable without code changes!'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)


def _get_processor(processor_type: str):
    """
    Factory function to create processors
    
    This function demonstrates how easy it is to add new processors
    without breaking existing code (Open-Closed Principle too!)
    """
    if processor_type == 'stripe':
        return StripeProcessor('sk_test_stripe_demo')
    elif processor_type == 'paypal':
        return PayPalProcessor('paypal_demo_client', 'paypal_demo_secret')
    else:
        raise ValueError(f"Unknown processor type: {processor_type}")


def lsp_explanation(request):
    """
    View that explains LSP with the payment processor example
    """
    context = {
        'principle': 'Liskov Substitution Principle',
        'definition': 'Objects of a superclass should be replaceable with objects of a subclass without breaking the application.',
        'payment_example': {
            'interface': 'PaymentProcessor',
            'implementations': ['StripeProcessor', 'PayPalProcessor'],
            'method': 'process_payment(amount, token) -> PaymentResult',
            'benefit': 'Same PaymentService code works with both processors'
        },
        'violations_prevented': [
            'Different method names (charge_card vs process_payment)',
            'Different parameters (card_token vs paypal_token)',
            'Different return types (dict vs object)',
            'Different error handling approaches'
        ]
    }
    
    return render(request, 'payments/lsp_explanation.html', context)