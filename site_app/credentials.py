import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class MpesaC2bCredential:
    consumer_key = 'U7MzaVlmhJYNt5GfHAJmwWkiw4MdaB4UDiI8eRvNGBWNbXcy'
    consumer_secret = 'gFA82oxUstdmHTLyXvC9Uwna5POUrYcN7BMBSXTRidTvyiB9kWla9fUQ282LrPHj'
    api_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    # callback_url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    callback_url="https://95cb-102-209-136-66.ngrok-free.app/callback/"


class MpesaAccessToken:
    r = requests.get(MpesaC2bCredential.api_URL,
                     auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]


class LipanaMpesaPassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"
    OffSetValue = '0'
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    data_to_encode = Business_short_code + passkey + lipa_time
# encoding this string
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
