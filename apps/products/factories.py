from abc import ABC, abstractmethod
from decouple import config
from apps.payments.models import PaymentProcessor, StripeProcessor, PayPalProcessor
from .services import (
    ShippingService,
    TaxService,
    UspsShippingService,
    UsTaxService,
    DhlShippingService,
    VatTaxService,
)


class MarketplaceFactory(ABC):
    @abstractmethod
    def create_payment_processor(self) -> PaymentProcessor:
        pass

    @abstractmethod
    def create_shipping_service(self) -> ShippingService:
        pass

    @abstractmethod
    def create_tax_service(self) -> TaxService:
        pass


class UsMarketFactory(MarketplaceFactory):
    def create_payment_processor(self) -> PaymentProcessor:
        return StripeProcessor(api_key=config("STRIPE_API_KEY", default="test"))

    def create_shipping_service(self) -> ShippingService:
        return UspsShippingService()

    def create_tax_service(self) -> TaxService:
        return UsTaxService()


class EuMarketFactory(MarketplaceFactory):
    def create_payment_processor(self) -> PaymentProcessor:
        return PayPalProcessor(
            client_id=config("PAYPAL_CLIENT_ID", default="test"),
            client_secret=config("PAYPAL_CLIENT_SECRET", default="test"),
        )

    def create_shipping_service(self) -> ShippingService:
        return DhlShippingService()

    def create_tax_service(self) -> TaxService:
        return VatTaxService()
