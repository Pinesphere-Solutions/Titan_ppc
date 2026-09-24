
from pydantic import BaseModel, EmailStr, Field


class VendorItem(BaseModel):
    code: str
    name: str
    email: str | None = None


class VendorEmailUpdateRequest(BaseModel):
    email: EmailStr


class MaterialItem(BaseModel):
    code: str
    name: str


class MaterialCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)


class ModelItem(BaseModel):
    code: str
    name: str


class ModelCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)


class RackItem(BaseModel):
    code: str
    name: str


class RackCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)


class BinItem(BaseModel):
    code: str
    name: str


class BinCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
