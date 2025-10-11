from abc import ABC, abstractmethod


class ShippingService(ABC):
    @abstractmethod
    def create_shipment(self, address: str, order_details: dict) -> dict:
        pass


class TaxService(ABC):
    @abstractmethod
    def calculate_tax(self, amount: float, address: str) -> float:
        pass


# US Market Services
class UspsShippingService(ShippingService):
    def create_shipment(self, address: str, order_details: dict) -> dict:
        # Logic for USPS shipping
        return {"carrier": "USPS", "status": "shipped"}


class UsTaxService(TaxService):
    def calculate_tax(self, amount: float, address: str) -> float:
        # Logic for US tax calculation
        return amount * 0.07


# EU Market Services
class DhlShippingService(ShippingService):
    def create_shipment(self, address: str, order_details: dict) -> dict:
        # Logic for DHL shipping
        return {"carrier": "DHL", "status": "shipped"}


class VatTaxService(TaxService):
    def calculate_tax(self, amount: float, address: str) -> float:
        # Logic for VAT calculation
        return amount * 0.20
