""" Custom Datatypes useful for the REST calls 

Custom types are required to be defined to fetch custom API requests sent by the
frontend to the backend, because the structure of a JSON file is nested.
"""

from typing import List
from pydantic import BaseModel

class Item(BaseModel):
    name: int

class ItemList(BaseModel):
    items: List[Item]