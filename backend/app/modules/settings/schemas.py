from pydantic import BaseModel, EmailStr, Field


class RoleItem(BaseModel):
    id: str
    name: str


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class UserItem(BaseModel):
    id: str
    username: str
    role_id: str
    role_name: str


class UserCreateRequest(BaseModel):
    # Treated as the user's email (see auth.models.User docstring) — this
    # is what M1 Forgot Password sends the reset link to, so new users
    # must be created with a real, valid email address here.
    username: EmailStr
    password: str = Field(min_length=8)
    role_id: str


class UserUpdateRoleRequest(BaseModel):
    role_id: str
