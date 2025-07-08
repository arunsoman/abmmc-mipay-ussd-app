from src.services.services import AuthService, BankingService, TopupService, BillPaymentService, BundleService
from typing import Union

class ServiceRegistry:
    _services = {
        "auth": AuthService(),
        "banking": BankingService(),
        "topup": TopupService(),
        "bills": BillPaymentService(),
        "bundles": BundleService()
    }
    
    @classmethod
    def get_service(cls, service_name: str) -> BundleService | BankingService | TopupService | BillPaymentService | AuthService | None:
        return cls._services.get(service_name)