# eps_gateway/types.py

from typing import List, Optional
from pydantic import BaseModel
from enum import IntEnum

class EPS_TransactionType(IntEnum):
    WEB = 1
    ANDROID = 2
    IOS = 3

class ProductItem(BaseModel):
    ProductName: str
    NoOfItem: str
    ProductProfile: str
    ProductCategory: str
    ProductPrice: str

class TransactionLog(BaseModel):
    status: str
    MerchantTransactionId: Optional[str] = None
    EPSTransactionId: Optional[str] = None
    TotalAmount: Optional[str] = None
    StoreAmount: Optional[str] = None
    FinancialEntity: Optional[str] = None
    message: Optional[str] = None

    def is_success(self) -> bool:
        return self.status.lower() == "success"

    def get_message(self) -> Optional[str]:
        return self.message

    def get_paid_amount(self) -> Optional[str]:
        return self.TotalAmount if self.is_success() else "0.00"

    def to_json(self, *args, **kwargs) -> str:
        return self.model_dump_json(*args, **kwargs)

class TransactionStatus(BaseModel):
    status: str
    MerchantTransactionId: str
    EPSTransactionId: str
    paid_amount: str
    received_amount: str
    payment_method: str
    message: Optional[str] = None

    def is_success(self) -> bool:
        return self.status.lower() == "success"

    def get_message(self) -> Optional[str]:
        return self.message

    def get_paid_amount(self) -> str:
        return self.paid_amount

    def to_json(self, *args, **kwargs) -> str:
        return self.model_dump_json(*args, **kwargs)

class PaymentPayload(BaseModel):
    merchantId: str
    storeId: str
    CustomerOrderId: str
    merchantTransactionId: str
    transactionTypeId: EPS_TransactionType = EPS_TransactionType.WEB
    totalAmount: float
    successUrl: str
    failUrl: str
    cancelUrl: str
    customerName: str
    customerEmail: str
    customerAddress: str
    customerAddress2: Optional[str] = None
    customerCity: str
    customerState: str
    customerPostcode: str
    customerCountry: str
    customerPhone: str
    shipmentName: Optional[str] = None
    shipmentAddress: Optional[str] = None
    shipmentAddress2: Optional[str] = None
    shipmentCity: Optional[str] = None
    shipmentState: Optional[str] = None
    shipmentPostcode: Optional[str] = None
    shipmentCountry: Optional[str] = None
    valueA: Optional[str] = None
    valueB: Optional[str] = None
    valueC: Optional[str] = None
    valueD: Optional[str] = None
    shippingMethod: Optional[str] = None
    noOfItem: Optional[str] = None
    productName: str
    productProfile: Optional[str] = None
    productCategory: Optional[str] = None
    ProductList: Optional[List[ProductItem]] = None
    financialEntityId: Optional[int] = 0
    transitionStatusId: Optional[int] = 0
    ipAddress: Optional[str] = None
    version: Optional[str] = "1"
    description: Optional[str] = None

class InitPaymentResponse(BaseModel):
    TransactionId: str
    RedirectURL: str
    ErrorMessage: Optional[str] = None
    ErrorCode: Optional[str] = None
    FinancialEntityList: Optional[str] = None    
