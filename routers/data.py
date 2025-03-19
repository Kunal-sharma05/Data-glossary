from fastapi import APIRouter, Depends, HTTPException, status
from db.database import get_db
from models.data import Data
from sqlmodel import Session
from typing import List, Annotated, Any
from crud.data import add_data, get_data

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/create_data", status_code=status.HTTP_201_CREATED, response_model=None)
def create_data(url: str, db: Session = Depends(get_db)) -> Any:
    try:
        add_data(url, db)
        return {"message": "Data added successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/get_data", response_model=None)
def retrieve_data(table_name: str, db: Session = db_dependency) -> Any:
    try:
        data_entries = get_data(table_name, db)
        return data_entries
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
