from db.database import base
from sqlalchemy import Integer, Column, ForeignKey, String, Text


class SessionData(base):
    __tablename__ = "session_data"

    session_id = Column(Integer, primary_key=True, index=True)
    human_messages = Column(Text)
    ai_messages = Column(Text)
    user_id = Column(Integer, ForeignKey("user_details.user_id"))
