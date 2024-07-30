from typing import List, Union
from pydantic import conlist, Field, field_validator
from typing_extensions import Annotated
from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Optional

class UpdateTeacherInfo(BaseModel):
    name: str
    last_name: str
    qualification: str

class PasswordResetRequest(BaseModel):
    old_password: Annotated[str, StringConstraints(min_length=8)]
    new_password: Annotated[str, StringConstraints(min_length=8)]


class SiteUserCreate(BaseModel):
    email: EmailStr
    password: str