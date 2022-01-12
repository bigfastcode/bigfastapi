from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from . import schema as _schemas
import json

app = APIRouter(tags=["Geo"])

app.get("/countries", response_model=_schemas.Country, status_code=200)
def get_countries():
    """Get Countries and their respective states

    Args:
        country_name (str): serves as a filter for a particular country

    Returns:
        List[Country]: list of countries and their respective states

    """
    with open("data/geo.json") as file:
        countries = json.load(file)
        for country in countries:
            del country["states"]
            del country["dial_code"]
    return JSONResponse(status_code=status.HTTP_200_OK, content=countries)


app.get("/countries/{country}/states", response_model=_schemas.State, status_code=200)
def get_country_states(country:str):
    """Get states within a particular country

    Args:
        country_name (str): serves as a filter for a particular country

    Returns:
        List[State]: list of states and their respective cities

    """
    with open("data/geo.json") as file:
        countries = json.load(file)
        country_data = list(filter(lambda data: data["name"].casefold() == country.casefold(), countries))
        if country_data:
            del country_data['dial_code']
            return JSONResponse(status_code=status.HTTP_200_OK, content=country)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    
app.get("/countries/dial-codes", response_model=_schemas.Country, status_code=200)
def get_countries_dial_Codes():
    """Get Countries and their respective dial codes

    Args:
        country_name (str): serves as a filter for a particular country

    Returns:
        List[Country]: list of countries and their respective dial codes

    """
    with open("data/geo.json") as file:
        countries = json.load(file)
        for country in countries:
            if country["dial_code"] == "":
                del country["dial_code"]
            del country["states"]
    return JSONResponse(status_code=status.HTTP_200_OK, content=countries)