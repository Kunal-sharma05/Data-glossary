from db.database import base
from sqlalchemy import Column, Integer, Enum, String
from models.UserRole import UserRole


class UserDetails(base):
    __tablename__ = "user_details"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)

    def __str__(self):
        return (f"id - {self.user_id}"
                f" name - {self.name}"
                f" email - {self.email}"
                f" password - {self.password}"
                f" role - {self.email}")