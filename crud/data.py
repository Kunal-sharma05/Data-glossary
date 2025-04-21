from fastapi import HTTPException, status
from db.database import db_dependency
from models.Session import SessionData
from schemas.session import SessionData as SessionDataDTO


def get_users(db: db_dependency):
    return db.query(SessionData).all()


def get_user_by_id(user_id: int, db: db_dependency):
    return db.query(SessionData).filter(SessionData.session_id_id == user_id).first()


def delete_user_by_id(user_id: int, db: db_dependency):
    db.query(SessionData).filter(SessionData.session_id == user_id).delete()
    db.commit()


def add_user(session_data: SessionDataDTO, db: db_dependency) -> int:
    session = SessionData(**session_data.model_dump())
    db.add(session)
    db.commit()
    return session.session_id


def update_user(user_id: int, session_data: SessionDataDTO, db: db_dependency):
    session = db.query(SessionData).filter(SessionData.session_id == user_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for key, value in session_data.model_dump().items():
        setattr(session, key, value)

    db.commit()
    db.refresh(session)
    return session
