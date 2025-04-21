import json
from fastapi import APIRouter, HTTPException, status, Request
from utility.Data_glossary import llm_call
from pydantic import BaseModel
from db.database import db_dependency
from typing import Dict, List
from schemas.session import SessionData as SessionDataDTO
from crud import data as session_service
from langchain_core.messages import HumanMessage, AIMessage
from utility.logic import compiled_app

router = APIRouter(
    tags=["LLM RESPONSE"]
)

session_store: Dict[str, List[Dict[str, str]]] = {}


class UserQuery(BaseModel):
    session_id: str
    question: str


@router.post("/chat")
def chat_with_memory(data: UserQuery):
    session_id = data.session_id
    question = data.question

    # Get or initialize session history
    history = session_store.get(session_id, [])

    # Run the LangGraph chain
    state_input = {"input": question, "history": history}
    result = compiled_app.invoke(state_input)

    # Update session history
    session_store[session_id] = result['history']

    return {
        "answer": result["answer"],
        "session_id": session_id,
        "history": result["history"]
    }


class ResponseModel(BaseModel):
    answer: str


@router.post("/ask_question", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def post_question(request: Request, prompt: str, db: db_dependency) -> ResponseModel:
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access"
        )
    else:
        user_id = user_session["id"]
        session_id = user_session["session_id"]
        try:
            response = llm_call(prompt=prompt)
            print(response.get("metadata"))
            history = response.get("metadata")

            human_messages = [item.content for item in history if isinstance(item, HumanMessage)]
            ai_messages = [item.content for item in history if isinstance(item, AIMessage)]
            print(f"human message is {human_messages} \n")
            print(f"AI message is {ai_messages} \n")

            session_model = SessionDataDTO(
                session_id=session_id,
                human_messages=json.dumps(human_messages),
                ai_messages=json.dumps(ai_messages),
                user_id=user_id,
            )
            session_service.update_user(session_id, session_model, db)

            return ResponseModel(answer=response.get("answer"))
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"An unexpected error occurred: {str(e)}")
