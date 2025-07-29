import requests
import json
from typing import List, Optional, Union
from . import config
from .utils import generate_hash
from .eps_types import ProductItem, TransactionLog, TransactionStatus, PaymentPayload, InitPaymentResponse


class EPSClient:
    def __init__(self):
        # Initialize with no token. Token will be fetched via get_token().
        self.token: Optional[str] = None

    def _handle_error(self, message: str, exception: Optional[Exception] = None) -> str:
        """
        Formats and returns a JSON error message string.
        Optionally includes the exception detail.
        """
        import json
        error_data = {
            "status": "failed",
            "message": f"{message}"
        }
        if exception:
            error_data["exception"] = str(exception)
        return json.dumps(error_data)

    def _safe_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        json_data: dict = None,
        timeout: int = 10,
        parse_json: bool = True
    ) -> Union[dict, str]:
        """
        Makes an HTTP request with proper error handling and returns the response.
        Returns a parsed JSON dictionary or error JSON string.
        """
        try:
            response = requests.request(method, url, headers=headers, json=json_data, timeout=timeout)
            response.raise_for_status()
            return response.json() if parse_json else response.text

        except requests.exceptions.Timeout:
            return self._handle_error("Connection timed out. The server may be down or slow.")
        except requests.exceptions.ConnectionError as e:
            return self._handle_error("Connection error: Failed to communicate with the payment gateway.", e)
        except requests.exceptions.HTTPError as e:
            return self._handle_error("HTTP error occurred: Failed to communicate with the payment gateway.", e)
        except requests.exceptions.RequestException as e:
            return self._handle_error("Request Error: Failed to communicate with the payment gateway.", e)
        except Exception as e:
            return self._handle_error("Unexpected error: Failed to communicate with the payment gateway.", e)

    def get_token(self) -> Optional[str]:
        """
        Authenticates using credentials and retrieves a bearer token.
        Returns the token if successful, or an error JSON string if failed.
        """
        x_hash = generate_hash(config.USERNAME, config.HASH_KEY)
        headers = {"x-hash": x_hash}
        body = {"userName": config.USERNAME, "password": config.PASSWORD}

        result = self._safe_request("POST", config.TOKEN_URL, headers=headers, json_data=body)
        
        if isinstance(result, dict) and "token" in result:
            self.token = result["token"]
            return self.token

        return result  # Return error response as JSON string

    def init_payment(self, payload: PaymentPayload, products: List[ProductItem]) -> InitPaymentResponse:
        """
        Initializes a payment request with given payload and product list.
        Returns the API response as InitPaymentResponse object.
        """
        if not self.token:
            self.get_token()

        tx_id = payload.merchantTransactionId
        x_hash = generate_hash(tx_id, config.HASH_KEY)

        headers = {
            "x-hash": x_hash,
            "Authorization": f"Bearer {self.token}",
        }

        # Create body from payload and ensure merchantId/storeId from config if not provided
        body = payload.dict()
        if not body.get("merchantId"):
            body["merchantId"] = config.MERCHANT_ID
        if not body.get("storeId"):
            body["storeId"] = config.STORE_ID
        
        # Add ProductList
        body["ProductList"] = [product.dict() for product in products]

        result = self._safe_request("POST", config.INIT_PAYMENT_URL, headers=headers, json_data=body)
        if isinstance(result, str):  # If result is error string
            return InitPaymentResponse(
                TransactionId="",
                RedirectURL="",
                ErrorMessage=result
            )

        if error_msg := result.get("ErrorMessage"):
            return InitPaymentResponse(
                TransactionId=result.get("TransactionId", ""),
                RedirectURL=result.get("RedirectURL", ""),
                ErrorMessage=error_msg,
                ErrorCode=result.get("ErrorCode"),
                FinancialEntityList=result.get("FinancialEntityList")
            )

        return InitPaymentResponse(**result)

    def get_transaction_log(self, merchant_transaction_id: str) -> TransactionLog:
        """
        Retrieves the full transaction log using the provided merchant transaction ID.
        Returns a TransactionLog object or an error.
        """
        if not self.token:
            self.get_token()

        x_hash = generate_hash(merchant_transaction_id, config.HASH_KEY)
        headers = {
            "x-hash": x_hash,
            "Authorization": f"Bearer {self.token}",
        }

        url = f"{config.VERIFY_URL}?merchantTransactionId={merchant_transaction_id}"
        result = self._safe_request("GET", url, headers=headers)

        if isinstance(result, str):  # If result is error string
            return TransactionLog(status="error", message=result)

        if not result.get("MerchantTransactionId"):
            return TransactionLog(status="error", message="Invalid Transaction ID")

        # Convert status to lowercase and return transaction log
        status = result.pop("Status", "").lower()
        return TransactionLog(status=status, **result)

    def get_transaction_status(self, merchant_transaction_id: str) -> TransactionStatus:
        """
        Extracts and formats the key details (status, amount, etc.) from the transaction log.
        Returns a concise TransactionStatus object.
        """
        try:
            log = self.get_transaction_log(merchant_transaction_id)
            if log.status == "error":
                return TransactionStatus(
                    status=log.status,
                    MerchantTransactionId=merchant_transaction_id,
                    EPSTransactionId="Unknown",
                    paid_amount="0.00",
                    received_amount="0.00",
                    payment_method="Unknown",
                    message=log.get_message()
                )

            status = getattr(log, "status", "unknown")
            gateway_trx_id = getattr(log, "EPSTransactionId", "Unknown") or "Unknown"
            paid_amount = getattr(log, "TotalAmount", "0.00") or "0.00"
            received_amount = getattr(log, "StoreAmount", "0.00") or "0.00"
            payment_method = getattr(log, "FinancialEntity", "Unknown") or "Unknown"

            return TransactionStatus(
                status=str(status).lower(),
                MerchantTransactionId=str(merchant_transaction_id),
                EPSTransactionId=str(gateway_trx_id),
                paid_amount=str(paid_amount) if status == "success" else "0.00",
                received_amount=str(received_amount) if status == "success" else "0.00",
                payment_method=str(payment_method)
            )

        except Exception as e:
            return TransactionStatus(
                status="error",
                MerchantTransactionId=merchant_transaction_id,
                EPSTransactionId="Unknown",
                paid_amount="0.00",
                received_amount="0.00",
                payment_method="Unknown",
                message=str(e)
            )
