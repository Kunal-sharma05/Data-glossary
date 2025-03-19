from sqlmodel import SQLModel, Field
from typing import Optional


class Data(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    table_name: str = Field(default=None, index=True)
    field_name: str = Field(index=True, min_length=5)
    description: str
    data_element: str
    checkTable: str
    datatype: str
    Length: int
    Decimals: int | None = Field(default=0)
