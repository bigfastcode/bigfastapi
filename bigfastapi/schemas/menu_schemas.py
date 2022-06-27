
import pydantic as pydantic


class MenuRequest(pydantic.BaseModel):
    menu_item: str
