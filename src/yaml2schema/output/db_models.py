# generated by datamodel-codegen:
#   filename:  input/anvil.yaml
#   timestamp: 2021-11-01T16:28:30+00:00

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Users(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    enabled: Optional[bool] = None
    signed_up: Optional[datetime] = None
    password_hash: Optional[str] = None
    confirmed_email: Optional[bool] = None
    email_confirmation_key: Optional[str] = None
    last_login: Optional[datetime] = None


class Phone(BaseModel):
    number: Optional[str] = None
    created_by: Optional[Users] = None
    created_on: Optional[datetime] = None


class Email(BaseModel):
    address: Optional[str] = None
    created_by: Optional[Users] = None
    created_on: Optional[datetime] = None


class Contact(BaseModel):
    name: Optional[str] = None
    phone: Optional[Phone] = None
    created_by: Optional[Users] = None
    email_list: Optional[List[Email]] = None
    address_listint: Optional[List[int]] = None
    age: Optional[int] = None
    created_on: Optional[datetime] = None
    father: Optional[Contact] = None


Contact.update_forward_refs()
