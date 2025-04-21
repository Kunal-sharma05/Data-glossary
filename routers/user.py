from fastapi import APIRouter, Depends, status, HTTPException, Query, Path, Request
from crud import user as user_service
from db.database import db_dependency, get_db
from typing import Annotated, Dict
from sqlalchemy.orm import Session
from core import security
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import UserDetailsIn
from schemas.session import SessionData
from crud import data as session_service

router = APIRouter(
    tags=["User Data"]
)


@router.options("/token")
async def handle_options():
    return {"message": "Preflight request handled"}


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(request: Request, db: db_dependency):
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access"
        )
    else:
        return user_service.get_users(db)


@router.post("/user_details", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user_details_request: UserDetailsIn, db: db_dependency):
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access"
        )
    else:
        user_service.add_user(user_details_request, db)


@router.put("/user_details/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_details(db: db_dependency, user_details_request: UserDetailsIn, user_id: int = Path(gt=0)):
    user_service.update_user_by_id(user_id, user_details_request, db)


@router.delete("/user_details/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_details(db: db_dependency, user_id: int = Query(gt=0)):
    user_details_model = user_service.get_user_by_id(user_id, db)
    if user_details_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nor found")
    else:
        user_service.delete_user_by_id(user_id, db)


@router.put("/token")
async def login_form(request: Request, db: db_dependency, email: str, password: str):
    user = await security.authenticate_user(email, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    session_model = SessionData(
        user_id=user.user_id,
    )
    session_id = session_service.add_user(session_model, db)
    request.session["user"] = {
        "id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "session_id": session_id
    }
    return request.session["user"]


@router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email")

    # Update the user's password
    user.password = security.hashing_password(new_password)
    db.commit()

    return {"message": "Password has been reset successfully."}


@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request) -> Dict:
    request.session.clear()
    return {"message": "Logged out successfully"}
