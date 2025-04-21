from passlib.context import CryptContext
from db.database import db_dependency
from crud import user as user_service

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def authenticate_user(email: str, password: str, db: db_dependency):
    user = user_service.get_user_by_email(email, db)
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    else:
        return user


def hashing_password(password: str):
    password = bcrypt_context.hash(password)
    return password
