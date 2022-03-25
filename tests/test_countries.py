from unittest import result
import pytest
import os
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_all_countries():
    response = client.get("/countries")
    assert response.status_code == 200
    assert type(response.json()) == list
    assert response.json()[0].get("dial_code",None) == None
    assert response.json()[0].get("sample_phone_format",None) == None
    assert response.json()[0].get("states",None) == None
    assert response.json()[0].get("name")
    assert response.json()[0].get("flag_url")
    assert response.json()[0].get("flag_unicode")
    
    
def test_country_states_success():
    response = client.get("/countries/Ng/states")
    assert response.status_code == 200
    result = response.json()
    assert type(result) == dict
    assert result.get("name") == "Nigeria"
    assert result.get("dial_code",None) == None
    assert type(result.get("states")) == list
    assert result.get("flag_url")
    assert result.get("flag_unicode")


def test_country_states_failure():
    response = client.get("/countries/Ngl/states")
    assert response.status_code == 404
    assert response.json() == {"detail": "Country not found"}

def test_countries_codes():
    response = client.get("/countries/codes")
    result = response.json()
    assert type(result) == list
    assert result[0].get("dial_code")
    assert result[0].get("states",None) == None
    assert result[0].get("name")
    assert result[0].get("flag_url") == None
    assert result[0].get("flag_unicode") == None
    
    
def test_country_codes_success():
    response = client.get("/countries/codes?country_code=Ng")
    result =  response.json()
    assert type(result) == dict
    assert result.get("name") == "Nigeria"
    assert result.get("dial_code") == "+234"
    assert result.get("states",None) == None
    assert len(result.get('sample_phone_format')) == 10
    assert result.get("flag_url") == None
    assert result.get("flag_unicode") == None

def test_country_codes_failure():
    response = client.get("/countries/codes?country_code=Ngl")
    assert response.status_code == 404
    assert response.json() == {"detail": "Country not found"}