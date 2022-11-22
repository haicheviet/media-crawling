import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class ItemBase(BaseModel):
    source: Optional[str] = None
    shared_from: Optional[str] = None
    last_update: Optional[datetime.date] = None
    text: Optional[str] = None
    reactions: Optional[int] = None
    reactions: Optional[int] = None
    reactions: Optional[int] = None
    reactions: Optional[int] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    title: str
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Item(ItemInDBBase):
    pass


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass
