from abc import ABC, abstractmethod


class BasePaymentGateway(ABC):
    """
    Abstract base class for payment gateways.
    All payment gateways should inherit from this class and implement the required methods.
    """

    @abstractmethod
    def initiate_payment(
        self, amount: float, success_url: str, failuire_url: str
    ) -> bool:
        """
        Process a payment of the specified amount in the specified currency.

        :param amount: The amount to be charged.
        :param currency: The currency in which the payment is made.
        :return: True if the payment was successful, False otherwise.
        """
        pass

    @abstractmethod
    def validate_payment(self, data: str) -> bool:
        """
        Refund a payment based on the transaction ID.

        :param transaction_id: The ID of the transaction to be refunded.
        :return: True if the refund was successful, False otherwise.
        """
        pass
