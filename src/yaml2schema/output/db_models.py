# generated by datamodel-codegen:
#   filename:  input/anvil.yaml
#   timestamp: 2022-05-11T14:03:41+00:00

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Categories(BaseModel):
    name: Optional[str] = None


class Articles(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    category: Optional[Categories] = None
