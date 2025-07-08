from typing import Dict, Any, cast

class AuthService:
    def validate_pin(self, msisdn: str, pin: str) -> bool:
        # Connect to authentication system/database
        # Return True if valid, False otherwise
        return pin == "123456"  # Demo implementation

    def change_pin(self, msisdn: str, new_pin: str) -> bool:
        # Update PIN in database
        return True  # Demo implementation

class BankingService:
    def get_balance(self, msisdn: str, bank_id: str) -> float:
        # Connect to bank API
        # Return balance
        return {
            "maiwand": 5000.0,
            "nkb": 3500.0,
            "azizi": 2800.0
        }.get(bank_id, 0.0)

    def transfer(self, msisdn: str, bank_id: str, amount: float, direction: str) -> bool:
        # Execute bank transfer
        return True  # Demo implementation

class TopupService:
    def topup_self(self, msisdn: str, amount: float) -> bool:
        # Process self top-up
        return True
    
    def topup_others(self, msisdn: str, target_number: str, amount: float) -> bool:
        # Process others top-up
        return True
    
    def topup_phone(self, msisdn: str, phone_number: str, amount: float) -> Dict:
        # Process phone top-up
        return {}

class BillPaymentService:
    def pay_bill(self, msisdn: str, biller: str, amount: float) -> bool:
        # Process bill payment
        return True

class BundleService:
    def purchase_bundle(self, msisdn: str, bundle_type: str, bundle_sku: str) -> dict:
        # Process bundle purchase
        return {}
    
    def get_balance(self, msisdn: str) -> float:
        # Get current bundle balance
        return 100.0