from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from app.models.question import QuestionResponse, CreateQuestionDto
from typing import List

class QuestionController:
    @staticmethod
    async def list_questions() -> List[QuestionResponse]:
        client = get_supabase_client()
        response = client.table("questions").select("*").execute()
        return [QuestionResponse.model_validate(item) for item in response.data]

    @staticmethod
    async def create_question(user_id: str, question: CreateQuestionDto) -> QuestionResponse:
        client = get_supabase_client()
        payload = question.model_dump()
        payload["user_id"] = user_id
        response = client.table("questions").insert(payload).execute()  # type: ignore
        if not response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao criar pergunta")
        return QuestionResponse.model_validate(response.data[0])
