import json
from fastapi import status, HTTPException
import requests
from bigfastapi.utils import settings

get_anchor_url = settings.ANCHOR_API_URL
anchor_test_key = settings.ANCHOR_TEST_KEY

headers = {
    "accept": "application/json",
    "x-anchor-key": anchor_test_key
}

def verify_nuban(bank_code: str, nuban: str):
    url = f"{get_anchor_url}api/v1/payments/verify-account/{bank_code}/{nuban}"
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def fetch_nigerian_banks(search_val: str=""):
    url = f"{get_anchor_url}api/v1/banks"
    response = requests.get(url, headers=headers)
    if search_val == "":
        return json.loads(response.text)
    else:
        return "search value"