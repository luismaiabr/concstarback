from fastapi import APIRouter
from typing import List
from app.models.question import QuestionResponse, CreateQuestionDto
from app.controllers.question_controller import QuestionController

router = APIRouter(prefix="/api/v1/questions", tags=["Questions"])

@router.get("/", response_model=List[QuestionResponse])
async def list_questions():
    return await QuestionController.list_questions()

@router.post("/", response_model=QuestionResponse)
async def create_question(user_id: str, question: CreateQuestionDto):
    return await QuestionController.create_question(user_id, question)
