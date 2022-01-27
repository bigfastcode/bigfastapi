
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
import qrcode as _qrcode
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
from bigfastapi.schemas.countries_schemas import Country, State


app = APIRouter(tags=["qrcode"])


@app.get("/qrcode", response_model=Country, status_code=200)
def get_qrcode():
    """Get Countries and their respective states

    Args:
        country_name (str): serves as a filter for a particular country

    Returns:
        List[Country]: list of countries and their respective states

    """
    data = "emediong"
    # img = _qrcode.make(data)
    # img.save("qr.png")
    # Creating an instance of QRCode class
    qr = _qrcode.QRCode(version = 1,
                    box_size = 10,
                    border = 5)
    
    # Adding data to the instance 'qr'
    qr.add_data(data)
    
    qr.make(fit = True)
    img = qr.make_image(fill_color = 'red',
                        back_color = 'white')
    print ("tiny")
    img.show()
    """img.save('MyQRCode2.png')"""
    return JSONResponse(status_code=status.HTTP_200_OK, content=img)

