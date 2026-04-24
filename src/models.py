from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerEvent(BaseModel):
    """Schema for a customer registration event from the Customers Topic.

    Validates incoming messages and applies transformations (whitespace
    stripping, name casing, email lowercasing) so the consumer can insert
    straight into the customers table
    """

    customer_id: UUID
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    age: int = Field(ge=18, le=120)
    email: EmailStr
    country: str = Field(min_length=1)
    city: str = Field(min_length=1)
    postal_code: str = Field(min_length=1)
    phone_number: str | None = None
    registration_date: datetime

    @field_validator("first_name", "last_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.strip().lower()