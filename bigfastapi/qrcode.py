
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
import qrcode as qrcode
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
from bigfastapi.schemas.qrcode_schemas import  State
import qrcode
from fastapi import APIRouter, status

import qrcode
from fastapi import APIRouter, status


app = APIRouter(tags=["qrcode"])


@app.get("/qrcode", status_code=status.HTTP_200_OK)
def get_qrcode(data: str):
    
    img = qrcode.make(data)
    type(img)  # qrcode.image.pil.PilImage
    img.show()
    img.save(f"bigfastapi\\data\\qrcode_images\\{data}.png")

    return "successfully created qrcode"