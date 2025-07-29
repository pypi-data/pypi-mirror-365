from np_payments.transport.httpx_sync import HTTPTransport
from np_payments.transport.httpx_async import AsyncHTTPTransport
from .scheams.esewa_schemas import ConstructEsewaRequest, EsewaDecodedResponse
from uuid import uuid4
import hmac
import hashlib
import base64
from typing import Optional, Union
from np_payments.base import BasePaymentGateway
import json


class _BaseEsewa(BasePaymentGateway):
    """
    Base class for Esewa payment gateway integration.
    This class provides the foundational methods and properties
    required for implementing the Esewa payment gateway.
    """

    def __init__(
        self,
        base_url: str,
        secret_key: str,
        success_url: str,
        failure_url: str,
        product_code: str,
        transport: Optional[Union[HTTPTransport, AsyncHTTPTransport]] = None,
    ):
        self.base_url = base_url
        self.secret_key = secret_key
        self.success_url = success_url
        self.failure_url = failure_url
        self.product_code = product_code
        self.transport = transport

    def _generate_signature(self, message: str, key: str) -> str:
        key = key.encode("utf-8")
        message = message.encode("utf-8")
        hmac_sha256 = hmac.new(key, message, hashlib.sha256)
        digest = hmac_sha256.digest()
        signature = base64.b64encode(digest).decode("utf-8")
        return signature

    def _build_request_payload(self, data: ConstructEsewaRequest, key: str) -> dict:
        if data.transaction_uuid is None:
            data.transaction_uuid = str(uuid4())

        signature_string = f"total_amount={data.total_amount},transaction_uuid={data.transaction_uuid},product_code={data.product_code}"
        signature = self._generate_signature(message=signature_string, key=key)

        payload = {
            "amount": str(data.amount),
            "success_url": data.success_url,
            "failure_url": data.failure_url,
            "product_code": data.product_code,
            "product_service_charge": data.product_service_charge,
            "product_delivery_charge": data.product_delivery_charge,
            "tax_amount": str(data.tax_amount),
            "total_amount": str(data.total_amount),
            "transaction_uuid": data.transaction_uuid,
            "signature": signature,
            "signed_field_names": "total_amount,transaction_uuid,product_code",
        }

        return payload

    def _build_payload(
        self,
        amount: float,
        success_url: Optional[str],
        failure_url: Optional[str],
        product_code: Optional[str],
        total_amount: Optional[float],
        product_service_charge: float,
        product_delivery_charge: float,
        tax_amount: float,
        transaction_uuid: Optional[str],
    ) -> dict:
        if not total_amount:
            total_amount = (
                amount + product_service_charge + product_delivery_charge + tax_amount
            )

        request = ConstructEsewaRequest(
            amount=amount,
            success_url=success_url or self.success_url,
            failure_url=failure_url or self.failure_url,
            product_code=product_code or self.product_code,
            product_service_charge=product_service_charge,
            product_delivery_charge=product_delivery_charge,
            tax_amount=tax_amount,
            total_amount=total_amount,
            transaction_uuid=transaction_uuid,
        )
        return self._build_request_payload(data=request, key=self.secret_key)

    def initiate_payment(
        self,
        amount: float,
        success_url: str,
        failure_url: str,
        product_code: str,
        total_amount: Optional[float] = None,
        product_service_charge: Optional[float] = 0.0,
        product_delivery_charge: Optional[float] = 0.0,
        tax_amount: Optional[float] = 0.0,
        transaction_uuid: Optional[str] = None,
    ) -> dict:
        if not total_amount:
            total_amount = (
                amount + product_service_charge + product_delivery_charge + tax_amount
            )

        requset = ConstructEsewaRequest(
            amount=amount,
            success_url=success_url,
            failure_url=failure_url,
            product_service_charge=product_service_charge,
            product_delivery_charge=product_delivery_charge,
            tax_amount=tax_amount,
            total_amount=total_amount,
            transaction_uuid=transaction_uuid,
        )
        payload = self._build_request_payload(data=requset, key=self.secret_key)

        response = self.transport.post(data=payload)
        return response

    def validate_payment(self, data: str) -> bool:
        decoded_data = json.loads(base64.b64decode(data).decode("utf-8"))
        data = EsewaDecodedResponse(**decoded_data)
        signature_string = f"transaction_code={data.transaction_code},status={data.status},total_amount={data.total_amount},transaction_uuid={data.transaction_uuid},product_code={data.product_code},signed_field_names={data.signed_field_names}"
        expected_signature = self._generate_signature(
            key=self.secret_key, message=signature_string
        )
        if expected_signature != data.signature:
            return False
        return True
