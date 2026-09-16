
from pydantic import BaseModel, EmailStr


class VendorItem(BaseModel):
    code: str
    name: str
    email: str | None = None


class VendorEmailUpdateRequest(BaseModel):
    email: EmailStr