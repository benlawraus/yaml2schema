# generated by datamodel-codegen:
#   filename:  input/anvil.yaml
#   timestamp: 2021-11-16T00:14:19+00:00

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Users(BaseModel):
    email: Optional[str] = None
    enabled: Optional[bool] = None
    signed_up: Optional[datetime] = None
    password_hash: Optional[str] = None
    confirmed_email: Optional[bool] = None
    email_confirmation_key: Optional[str] = None


class Email(BaseModel):
    address: Optional[str] = None
    created_by: Optional[Users] = None
    created_on: Optional[datetime] = None


class Phone(BaseModel):
    number: Optional[str] = None
    created_by: Optional[Users] = None
    created_on: Optional[datetime] = None


class Contact(BaseModel):
    name: Optional[str] = None
    phone: Optional[Phone] = None
    email: Optional[List[Email]] = None
    age: Optional[float] = None
    created_by: Optional[Users] = None
    created_on: Optional[datetime] = None
    family: Optional[List[int]] = None
    uid: Optional[int] = None
    father: Optional[Contact] = None


Contact.update_forward_refs()
