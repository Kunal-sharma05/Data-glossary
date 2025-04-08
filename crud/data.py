from fastapi import HTTPException, status
from models.data import DataCreate
from typing import Any
from db.database import db_dependency
from utility.scrap import scrape_table_from_url
from sqlmodel import select
import numpy as np


def add_data(url: str, db: db_dependency):
    table_name, df = scrape_table_from_url(url)
    df = df.replace({np.nan: None})
    for _, row in df.iterrows():
        data_entry = DataCreate(
            table_name=table_name,
            field_name=row.get("Field", None),
            description=row.get("Field.1", None),
            data_element=row.get("Data element", None),
            checkTable=row.get("Checktable", None),
            datatype=row.get("Datatype", None),
            Length=row.get("Length", None),
            Decimals=row.get("Decimals", None),
            Possible_values=row.get("Possible values", None)
        )
        print(data_entry)
        # db_data = Data.model_validate(data_entry)
        # print(db_data)
        db.add(data_entry)
    db.commit()
    print(f"Data saved to the database successfully in the table:- {table_name}")


def get_data(table_name: str, db: db_dependency) -> Any:
    try:

        statement = select(DataCreate).where(DataCreate.table_name == table_name)
        data_entries = db.exec(statement).all()

        if not data_entries:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found in the database.")

        return data_entries
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while "
                                                                                      f"fetching data: {str(e)}")
