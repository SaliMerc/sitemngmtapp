import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from django.conf import settings


class MpesaC2bCredential:
    consumer_key=settings.MPESA_CONSUMER_KEY
    consumer_secret=settings.MPESA_CONSUMER_SECRET
    api_URL=settings.MPESA_API_URL
    callback_url=settings.MPESA_CALLBACK_URL


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
