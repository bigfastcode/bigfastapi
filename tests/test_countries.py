import pytest
import os
import json

def get_JSON_data():
    with open("data/countries.json") as file:
        data = json.load(file)
        return data

def test_geo_file():
    assert os.path.isfile("data/countries.json")
    try:
        get_JSON_data()
    except Exception as e:
        print(e)
        assert False
        
        
@pytest.fixture
def get_countries_mock(mocker):
    mock_countries = mocker.patch("bigfastapi.countries.get_countries")
    data = get_JSON_data()
    for country in data:
        del country["states"]
        del country["dial_code"]
        del country['sample_phone_format']
    mock_countries.return_value = data
    return  mock_countries


@pytest.fixture
def get_country_states_mock(mocker):
    
    def side_effect(country:str):
        data = get_JSON_data()
        data_search = [country_data for country_data in data if country_data['name'].casefold() == country.casefold()]
        country_found = data_search[0] if data_search != [] else {}
        if country_found:
            del country_found["dial_code"]
        return country_found
    
    mock_country_states = mocker.patch("bigfastapi.countries.get_country_states", side_effect=side_effect)             
    return mock_country_states

@pytest.fixture
def get_countries_dial_codes_mock(mocker):
    
    def side_effect(country:str = None):
        data = get_JSON_data()
        if country:
            data_search = [country_data for country_data in data if country_data['name'].casefold() == country.casefold()]
            country_found = data_search[0] if data_search != [] else {}
            if country_found:
                if country_found["dial_code"] == "":
                    return {}
                del country_found["states"]
            return country_found
        
        for elem in data:
            if elem["dial_code"] == "":
                del elem["dial_code"]
            del elem["states"]
        return data
    
    mock_countries_dial_codes = mocker.patch("bigfastapi.countries.get_countries_dial_codes", side_effect=side_effect)
    return  mock_countries_dial_codes          

def test_geo_data():
    try:
       data = get_JSON_data()
    except Exception as e:
        print(e)
        assert False
    assert data[0].get("name", False)
    assert data[0].get("iso3", False)
    assert data[0].get("iso2", False)
    assert data[0].get("states", False)
    assert data[0].get("dial_code", False)
    assert data[0].get('sample_phone_format',False)
    
def test_country(get_countries_mock):
    response = get_countries_mock()
    assert type(response) == list 
    assert response[0].get("dial_code",None) == None
    assert response[0].get("sample_phone_format",None) == None
    assert response[0].get("states",None) == None
    assert response[0].get("name")
    
    
def test_country_states(get_country_states_mock):
    response = get_country_states_mock("Nigeria")
    assert type(response) == dict
    assert response.get("name") == "Nigeria"
    assert response.get("dial_code",None) == None
    assert type(response.get("states")) == list
    
def test_countries_dial_codes(get_countries_dial_codes_mock):
    response = get_countries_dial_codes_mock()
    assert type(response) == list
    assert response[0].get("dial_code")
    assert response[0].get("states",None) == None
    assert response[0].get("name")
    
def test_country_dial_code(get_countries_dial_codes_mock):
    response = get_countries_dial_codes_mock("Nigeria")
    assert type(response) == dict
    assert response.get("name") == "Nigeria"
    assert response.get("dial_code") == "+234"
    assert response.get("states",None) == None
    assert len(response.get('sample_phone_format')) == 10