import os

# Is in debug
IS_SANDBOX = os.getenv("IS_SANDBOX", "False").lower() == "true"

# EPS Gateway Configuration with Environment Variable Priority
MERCHANT_ID = os.getenv("EPS_MERCHANT_ID", "")
STORE_ID = os.getenv("EPS_STORE_ID", "")
USERNAME = os.getenv("EPS_USERNAME", "")
PASSWORD = os.getenv("EPS_PASSWORD", "")
HASH_KEY = os.getenv("EPS_HASH_KEY", "")

# EPS API Endpoints
if IS_SANDBOX:
    TOKEN_URL = os.getenv("EPS_TOKEN_URL", "https://sandboxpgapi.eps.com.bd/v1/Auth/GetToken")
    INIT_PAYMENT_URL = os.getenv("EPS_INIT_PAYMENT_URL", "https://sandboxpgapi.eps.com.bd/v1/EPSEngine/InitializeEPS")
    VERIFY_URL = os.getenv("EPS_VERIFY_URL", "https://sandboxpgapi.eps.com.bd/v1/EPSEngine/CheckMerchantTransactionStatus")
else:
    TOKEN_URL = os.getenv("EPS_TOKEN_URL", "https://pgapi.eps.com.bd/v1/Auth/GetToken")
    INIT_PAYMENT_URL = os.getenv("EPS_INIT_PAYMENT_URL", "https://pgapi.eps.com.bd/v1/EPSEngine/InitializeEPS")
    VERIFY_URL = os.getenv("EPS_VERIFY_URL", "https://pgapi.eps.com.bd/v1/EPSEngine/CheckMerchantTransactionStatus")
