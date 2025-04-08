from fastapi import APIRouter, HTTPException, status
from typing import List, Any, Dict
from utility.Data_glossary import llm_call

router = APIRouter(
    tags=["LLM RESPONSE"]
)


@router.post("/ask_question", status_code=status.HTTP_201_CREATED, response_model=Dict)
def post_question(prompt: str) -> Dict:
    try:
        response = llm_call(prompt=prompt)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred: {str(e)}")


