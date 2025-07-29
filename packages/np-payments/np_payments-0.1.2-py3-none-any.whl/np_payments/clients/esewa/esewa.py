from typing import Optional
from .base_esewa import _BaseEsewa
from np_payments.transport.httpx_sync import HTTPTransport


class EsewaClient(_BaseEsewa):
    """
    Sync Client class for interacting with the Esewa payment gateway.
    This class extends the base functionality provided by _BaseEsewa
    and can be used to implement specific payment operations.
    """

    def __init__(self, base_url, secret_key, success_url, failure_url, product_code):
        transport = HTTPTransport(base_url=base_url)
        super().__init__(
            base_url, secret_key, success_url, failure_url, product_code, transport
        )

    def initiate_payment(
        self,
        amount: float,
        success_url: Optional[str] = None,
        failure_url: Optional[str] = None,
        product_code: Optional[str] = None,
        total_amount: Optional[float] = None,
        product_service_charge: float = 0.0,
        product_delivery_charge: float = 0.0,
        tax_amount: float = 0.0,
        transaction_uuid: Optional[str] = None,
    ) -> dict:
        payload = self._build_payload(
            amount,
            success_url,
            failure_url,
            product_code,
            total_amount,
            product_service_charge,
            product_delivery_charge,
            tax_amount,
            transaction_uuid,
        )
        return self.transport.post(data=payload)
