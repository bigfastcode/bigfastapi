from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
# from . import schema as _schemas
from .schemas import countries_schemas as _schemas
import json

app = APIRouter(tags=["Countries"])


@app.get("/countries", response_model=_schemas.Country, status_code=200)
def get_countries():
    """Get Countries and their respective states

    Args:
        country_name (str): serves as a filter for a particular country

    Returns:
        List[Country]: list of countries and their respective states

    """
    with open("data/countries.json") as file:
        countries = json.load(file)
        for country in countries:
            del country["states"]
            del country["dial_code"]
            del country["sample_phone_format"]
    return JSONResponse(status_code=status.HTTP_200_OK, content=countries)


@app.get("/countries/{country_code}/states", response_model=_schemas.State, status_code=200)
def get_country_states(country_code: str):
    """Get states within a particular country

    Args:
        country_name (str): serves as a filter for a particular country

    Returns:
        List[State]: list of states and their respective cities

    """
    with open("data/countries.json") as file:
        countries = json.load(file)
        country_data = list(
            filter(
                lambda data: data["iso2"].casefold() == country_code.casefold()
                or data["iso3"].casefold() == country_code.casefold(),
                countries,
            )
        )
        if country_data:
            data = country_data[0]
            del data["dial_code"]
            del data["sample_phone_format"]
            return JSONResponse(status_code=status.HTTP_200_OK, content=data)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )


@app.get("/countries/codes", response_model=_schemas.Country, status_code=200)
def get_countries_dial_codes(country_code: str = None):
    """Get Countries and their respective codes
        including dial codes and sample phone formats

    Args:
        country (str): serves as a filter for a particular country

    Returns:
        List[Country]: list of countries and their respective dial codes

    """
    with open("data/countries.json") as file:
        countries = json.load(file)
        if country_code:
            country_search = list(
                filter(
                lambda data: data["iso2"].casefold() == country_code.casefold()
                or data["iso3"].casefold() == country_code.casefold(),
                countries,
            )
        )
            country_found = country_search[0] if country_search != [] else {}
            if country_found:
                if country_found["dial_code"] == "":
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Country not found",
                    )
                del country_found["states"]
                del country_found["flag_url"]
                del country_found["flag_unicode"]
                return JSONResponse(
                    status_code=status.HTTP_200_OK, content=country_found
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
            )

        for country_data in countries:
            if country_data["dial_code"] == "":
                del country_data
            del country_data["states"]
            del country_data["flag_url"]
            del country_data["flag_unicode"]
        return JSONResponse(status_code=status.HTTP_200_OK, content=countries)
