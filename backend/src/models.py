from pydantic import BaseModel
from typing import List, Optional


class Section(BaseModel):
    id: int
    name: str
    type: str
    code: str
    parent_section_id: Optional[int]
    children: List['Section'] = []

    class Config:
        orm_mode = True


class Work(BaseModel):
    id: int
    code: str
    end_name: str
    measure_unit: str

    class Config:
        orm_mode = True


class NameGroup(BaseModel):
    id: int
    begin_name: str

    class Config:
        orm_mode = True


class Item(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True


class WorkResourceData(BaseModel):
    resource_id: Optional[int]
    abstract_resource_id: Optional[int]
    service_resource_id: Optional[int]
    quantity: str
    measure_unit: Optional[str]
    resource_code: Optional[str]
    resource_end_name: Optional[str]
    abstract_resource_code: Optional[str]
    abstract_resource_name: Optional[str]
    service_resource_code: Optional[str]
    service_resource_name: Optional[str]

    class Config:
        orm_mode = True


class WorkDetail(BaseModel):
    id: int
    code: str
    end_name: str
    measure_unit: Optional[str]
    nr: Optional[str]
    sp: Optional[str]
    items: List[Item]
    resources: List[WorkResourceData]

    class Config:
        orm_mode = True
