from pydantic import BaseModel, Field

class QuestionRecord(BaseModel):
    userId: str = Field(..., description="ID único do usuário que registrou a bateria de questões")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data do registro das questões")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora do registro das questões")
    description: str = Field(..., min_length=1, description="Descrição textual das questões resolvidas")
    questionsCount: int = Field(..., ge=0, description="Quantidade total de questões resolvidas")

class CreateQuestionDto(BaseModel):
    amount: float = Field(..., description="Quantidade ou valor")
    description: str = Field(..., description="Descrição da pergunta")

class QuestionResponse(CreateQuestionDto):
    id: int
    user: str = Field(..., description="Nome ou ID do usuário criador")
    date: str
