
"""Countries

This file will list out all the countries in the world. You can
also retrieve the states and the phonecodes for all the countries.

Import it like this app.include_router(countries, tags=["Countries"])
After that, the following endpoints will become available:

 * /countries
 * /countries/{country_code}/states
 * /countries/codes

"""


import json
import pkg_resources
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
from .schemas.countries_schemas import Country, State


app = APIRouter(tags=["Countries"])

COUNTRIES_DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/')


@app.get("/countries", status_code=200)
def get_countries(search_value: str=""):
    """intro-->This endpoint returns a list of all countries in the world and their respective states. To get this data you need to make a get request to the /countries endpoint.

    returnDesc-->On sucessful request, it returns
        returnBody--> "an array country objects".
    """
    suggestions = []
    with open(COUNTRIES_DATA_PATH + "/countries.json") as file:
        countries = json.load(file)
        for country in countries:
            del country["states"]
            del country["dial_code"]
            del country["sample_phone_format"]
        if search_value == "":        
            return JSONResponse(status_code=status.HTTP_200_OK, content=countries)
        else:
            # result =  next((item for item in countries if item["name"] == search_value), [])
            # if result == []:
            for country in countries:
                if search_value in country["name"]:
                    suggestions.append(country)
    
            result = suggestions
            if type(result) == dict:
                return [result] 
            else:
                return result


@app.get("/countries/{country_code}/states", response_model=State, status_code=200)
def get_country_states(country_code: str):
    """intro-->This endpoint returns a list of all states in a queried country. To get this data you need to make a get request to the /countries/{country_code}/states endpoint.
    
    paramDesc-->On get request, the url takes a query parameter "country_code":
        param-->country_code: This is the country code of the country of interest

    returnDesc-->On sucessful request, it returns
        returnBody--> "an array of states".
    """
    with open(COUNTRIES_DATA_PATH + "/countries.json") as file:
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


@app.get("/countries/codes", response_model=Country, status_code=200)
def get_countries_dial_codes(country_code: str = None):
    """intro-->This endpoint returns a list of all countries and thier respective codes including dial codes and sample phone formats. To use this endpoint, you need to make a get request to the /countries/codes enpoint
    
    paramDesc-->To query for a particular country, you need to make a get request to /countries/codes endpoint and make query using the format /countries/codes?country_code={country_code}
        param-->country_code: This is the country code of the country of interest
    
    returnDesc-->On sucessful request, it returns
        returnBody--> an array of countries and their codes.
    """
    with open(COUNTRIES_DATA_PATH + "/countries.json") as file:
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
