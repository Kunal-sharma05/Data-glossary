from fastapi import Depends, HTTPException, status
from db.database import get_db
from models.data import Data
from typing import Annotated, Any
from sqlmodel import Session
from utility.scrap import scrape_table_from_url
from sqlmodel import select

db_dependency = Annotated[Session, Depends(get_db)]


def add_data(url: str, db: Session = Depends(get_db)):
    table_name, df = scrape_table_from_url(url)
    for _, row in df.iterrows():
        data_entry = Data(
            table_name=table_name,
            field_name=row.get("Field", None),
            description=row.get(" ", None),
            data_element=row.get("Data element", None),
            checkTable=row.get("Checktable", None),
            datatype=row.get("Datatype", None),
            Length=row.get("Length", None),
            Decimals=row.get("Decimals", None),
        )
        db.add(data_entry)
    db.commit()
    print(f"Data saved to the database successfully in the table:- {table_name}")


def get_data(table_name: str, db: Session = db_dependency) -> Any:
    try:

        statement = select(Data).where(Data.table_name == table_name)
        data_entries = db.exec(statement).all()

        if not data_entries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found in the database."
            )

        return data_entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching data: {str(e)}"
        )
