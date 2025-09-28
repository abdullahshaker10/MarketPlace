"""
Payment Models and Processors - LSP Implementation

All payment-related classes in one file for simplicity.
Demonstrates Liskov Substitution Principle with minimal code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PaymentResult:
    """
    Standardized payment result that all processors must return
    This ensures LSP compliance - same data structure from all processors
    """
    success: bool
    transaction_id: str
    amount: float
    processor_name: str
    error_message: Optional[str] = None
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.processor_name}: {status} - ${self.amount} (ID: {self.transaction_id})"


class PaymentProcessor(ABC):
    """
    Abstract interface for all payment processors
    
    LSP Key: Any subclass should be substitutable for this base class
    """
    
    @abstractmethod
    def process_payment(self, amount: float, payment_token: str) -> PaymentResult:
        """
        Process a payment - ALL processors must implement this exactly the same way
        
        Args:
            amount: Payment amount in dollars
            payment_token: Payment method token
            
        Returns:
            PaymentResult: Standardized result object
        """
        pass


class StripeProcessor(PaymentProcessor):
    """Stripe implementation following LSP"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.processor_name = "Stripe"
    
    def process_payment(self, amount: float, payment_token: str) -> PaymentResult:
        """
        Stripe implementation - same signature as interface
        """
        try:
            print(f"[STRIPE] Processing ${amount} with token {payment_token}")
            
            # Simulate Stripe API call
            stripe_response = {
                'charge_id': f'ch_stripe_{payment_token}',
                'status': 'succeeded',
                'amount': int(amount * 100)  # Stripe uses cents
            }
            
            return PaymentResult(
                success=stripe_response['status'] == 'succeeded',
                transaction_id=stripe_response['charge_id'],
                amount=amount,
                processor_name=self.processor_name
            )
            
        except Exception as e:
            return PaymentResult(
                success=False,
                transaction_id="",
                amount=amount,
                processor_name=self.processor_name,
                error_message=f"Stripe error: {str(e)}"
            )


class PayPalProcessor(PaymentProcessor):
    """PayPal implementation following LSP"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.processor_name = "PayPal"
    
    def process_payment(self, amount: float, payment_token: str) -> PaymentResult:
        """
        PayPal implementation - EXACT same signature as Stripe
        This is what makes them substitutable (LSP compliance)
        """
        try:
            print(f"[PAYPAL] Processing ${amount} with token {payment_token}")
            
            # Simulate PayPal API call
            paypal_response = {
                'payment_id': f'PAY_paypal_{payment_token}',
                'state': 'approved',
                'amount': {'total': str(amount), 'currency': 'USD'}
            }
            
            return PaymentResult(
                success=paypal_response['state'] == 'approved',
                transaction_id=paypal_response['payment_id'],
                amount=amount,
                processor_name=self.processor_name
            )
            
        except Exception as e:
            return PaymentResult(
                success=False,
                transaction_id="",
                amount=amount,
                processor_name=self.processor_name,
                error_message=f"PayPal error: {str(e)}"
            )


class PaymentService:
    """
    Service that works with ANY PaymentProcessor
    
    Perfect LSP demonstration - this class doesn't care which processor it uses!
    """
    
    def __init__(self, processor: PaymentProcessor):
        self.processor = processor
    
    def charge_customer(self, amount: float, payment_token: str) -> PaymentResult:
        """
        Process payment using any processor
        
        This method works identically with Stripe, PayPal, or any future processor!
        No if/elif statements needed - perfect LSP compliance.
        """
        return self.processor.process_payment(amount, payment_token)