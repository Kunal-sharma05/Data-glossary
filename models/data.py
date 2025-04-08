from sqlmodel import SQLModel, Field


class DataCreate(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    table_name: str = Field(default=None, index=True)
    field_name: str = Field(index=True, default=None)
    description: str | None = Field(default=None)
    data_element: str | None = Field(default=None)
    checkTable: str | None = Field(default=None)
    datatype: str | None = Field(default=None)
    Length: int | None = Field(default=None)
    Decimals: int | None = Field(default=None)
    Possible_values: str | None = Field(default=None)
#
#
# class Data(DataCreate, table=True):
#     id: int = Field(default=None,primary_key=True)
