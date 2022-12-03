from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

class Response():
    def __init__(self, message, status_code, data={}):
        self.message = message        
        self.status_code = status_code
        self.data = data if data else {}
       
        
    def __call__(self):
        # check if response code is a success code, then return success message, else send error msg
        
        if self.is_successful():
            return JSONResponse(
                {"message": self.message, "data": jsonable_encoder(self.data)}, 
                status_code=self.status_code
            )
        else:
            self.send_error_msg()


    def is_successful(self):
        if self.status_code in [200, 201, 202]:
            return True
        else:
            return False
            

    def send_error_msg(self):        
        raise HTTPException(
                    status_code=self.status_code,
                    detail=self.message,
                )        