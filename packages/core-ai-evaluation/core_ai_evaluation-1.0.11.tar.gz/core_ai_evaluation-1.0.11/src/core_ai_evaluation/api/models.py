from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    chat_model: str
    temperature: float
    system_instructions: str
