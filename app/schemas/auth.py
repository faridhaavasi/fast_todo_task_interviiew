import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class UserSetEmailRequest(BaseModel):
    email: EmailStr

class UserSetEmailResponse(BaseModel):
    email: EmailStr
    created_at: datetime.datetime
    updated_at: datetime.datetime

class UserSetPasswordRequest(BaseModel):
    password: str
    password_repeat: str


class UserSetPasswordResponse(BaseModel):
    email: EmailStr
    access_token: str
    refresh_token: str


