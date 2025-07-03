from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=16, json_schema_extra={"format": "password"})
    new_password: str = Field(..., min_length=16, json_schema_extra={"format": "password"})
    totp: str


class AuthInviteCreateRequest(BaseModel):
    code: Optional[str] = Field(None, description="Optional invite code. If not provided, a random code will be generated.")
    use_max: Optional[int] = Field(1, description="Maximum number of uses for the invite.")


class AuthInviteCreateResponse(BaseModel):
    code: str
    use_max: int


class AuthInviteStatusResponse(BaseModel):
    use_left: int

class InviteResponse(BaseModel):
    code: str
    use_left: int


class InviteListResponse(BaseModel):
    invites: List[InviteResponse]


# class AuthTokenOut(BaseModel):
#     id: UUID
#     user_id: int
#     token: str
#     created: datetime
#     expires: datetime

#     class Config:
#         orm_mode = True


# class CreateAuthToken(BaseModel):
#     user_id: int
#     token: str
#     expires: datetime

# User
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserOut(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    otp: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=16, json_schema_extra={"format": "password"})
    invite: str
    accept_terms: bool = Field(..., description="User must accept terms and conditions")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class RegisterResponse(BaseModel):
    user: UserResponse
    totp_uri: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=16, json_schema_extra={"format": "password"})

#Manufacturer
class ManufacturerBase(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerUpdate(ManufacturerBase):
    pass


class ManufacturerOut(ManufacturerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


#Application
class ApplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    manufacturer_id: int
    languagemodel_id: int
    modelchoice_id : int
    is_active: bool = True

class CreateApplication(ApplicationBase):
    pass

class ApplicationOut(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ApplicationWithManufacturerOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    manufacturer_id: int
    manufacturer_name: str
    languagemodel_id: int
    languagemodel_name: str
    modelchoice_id: int
    modelchoice_name: str
    applicationuser_id: int
    applicationuser_selected: bool

    model_config = {
        "from_attributes": True
    }

class ApplicationStats(BaseModel):
    total: int
    active: int

class ApplicationUserBase(BaseModel):
    application_id: int
    selected: bool

class ApplicationUserUpdate(ApplicationUserBase):
    pass


# LanguageModel
class LanguageModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class LanguageModelCreate(LanguageModelBase):
    pass

class LanguageModelUpdate(LanguageModelBase):
    pass

class LanguageModelOut(LanguageModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# Model Choice
class ModelChoiceBase(BaseModel):
    name: str

class ModelChoiceCreate(ModelChoiceBase):
    pass

class ModelChoiceUpdate(BaseModel):
    name: str | None = None

class ModelChoiceOut(ModelChoiceBase):
    id: int

    model_config = {
        "from_attributes": True
    }
