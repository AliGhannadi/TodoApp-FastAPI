from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal
from datetime import datetime, timezone
class TodoRequest(BaseModel):
    
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=200)
    priority: int = Field(gt=0, lt=11)
    complete: bool = Field(default=False) 
    scheduled_time: datetime # New Field
    @field_validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            v = v.replace(tzinfo=timezone.utc)
        if v < datetime.now(timezone.utc):
            raise ValueError('Scheduled time must be in the future.')
        return v
class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, example='john', description='Username must be between 3 \and 20 characters long.')
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2, max_length=30)
    last_name: str = Field(..., min_length=2, max_length=30)
    phone_number: str
    password: str = Field(min_length=6, max_length=20, example='strongPassword123!', description='Password must be between 6 and 20 characters long.')
    @field_validator('password')
    def validate_password(cls, value):
        if ' ' in value:
            raise ValueError('Password must not contain spaces.')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not any(char.isdigit() for char in value):  
            raise ValueError('Password must contain at least one digit.')
        return value
    
    role: Literal['user', 'admin'] = Field(
        default='user',
        title='User Role',
        description="Role of the user, can be either 'user' or 'admin'. Defaults to 'user'.",
        example='admin/user'
    )
    
class UpdatePhoneNumber(BaseModel):
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="New phone number. Must include country code.",
        example="+989123456789"
    )

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str