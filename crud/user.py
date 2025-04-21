from fastapi import HTTPException, status
from db.database import db_dependency
from models.user import UserDetails
from schemas.user import UserDetailsIn
from core import security


def get_users(db: db_dependency):
    return db.query(UserDetails).all()


def get_user_by_id(user_id: int, db: db_dependency):
    return db.query(UserDetails).filter(UserDetails.user_id == user_id).first()


def get_user_by_email(email: str, db: db_dependency):
    return db.query(UserDetails).filter(UserDetails.email == email).first()


def delete_user_by_id(user_id: int, db: db_dependency):
    db.query(UserDetails).filter(UserDetails.user_id == user_id).delete()
    db.commit()


def add_user(user_request: UserDetailsIn, db: db_dependency):
    user = UserDetails(**user_request.model_dump())
    password = user_request.password
    user.password = security.hashing_password(password)
    db.add(user)
    db.commit()


def update_user_by_id(user_id: int, user_details_request: UserDetailsIn, db: db_dependency):
    user = get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.name = user_details_request.name
    user.password = security.hashing_password(user_details_request.password)
    user.role = user_details_request.role
    user.email = user_details_request.email
    db.add(user)
    db.commit()
