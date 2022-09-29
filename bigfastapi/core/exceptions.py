import fastapi
from fastapi.exceptions import HTTPException


class UnauthorizedException(HTTPException):
    "Exception raised when a user is not granted permission"

    def __init__(self, message: str):
        super().__init__(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=message
            if message
            else "This user is not authorized to perform this action",
        )


class BadRequestException(HTTPException):
    "Exception raised when a bad request is triggered"

    def __init__(self, message: str):
        super().__init__(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=message
            if message
            else "This user is not authorized to perform this action",
        )
