from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    email: str | None = None
    phone: str
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_verified: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)