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