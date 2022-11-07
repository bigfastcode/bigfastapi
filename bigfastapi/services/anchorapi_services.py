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

def verify_nuban():
    return 'yes'

def fetch_nigerian_banks():
    url = f"{get_anchor_url}api/v1/banks"
    response = requests.get(url, headers=headers)
    return json.loads(response.text)