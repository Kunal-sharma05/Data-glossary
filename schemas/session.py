from pydantic import BaseModel
from typing import Optional, List


class SessionData(BaseModel):
    human_messages: Optional[str] = None
    ai_messages: Optional[str] = None
    user_id: int


