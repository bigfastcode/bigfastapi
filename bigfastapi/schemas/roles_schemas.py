from pydantic import BaseModel
from typing import Optional, List

class Role(BaseModel):
    organization_id: Optional[str]
    role_name: str

    class Config:
        orm_mode = True

class AddRole(Role):
    role_name: str