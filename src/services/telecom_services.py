from typing import Protocol

class TelcoService(Protocol):
    def __init__(self):
        pass

    def TopUpSelf(self, request, context):
        pass
        
        

    def TopUpOthers(self, request, context):
        pass

    def BuyBundleSelf(self, request, context):
        pass

    def BuyBundleOthers(self, request, context):
        pass

    def _process_bundle_purchase(self, request, target_number, context):
        pass