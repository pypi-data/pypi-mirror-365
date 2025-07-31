import os

import httpx

from core_ai_evaluation.evaluation.models import Answer, ModelInput
from core_ai_evaluation.shared.log import logger


class AnswerGenerator:
    def __init__(
        self,
        chat_model: str,
        temperature: float = 0.0,
        system_instructions: str | None = None,
        agent_name: str = "System-Agent",
        full_response: bool = False,
    ):
        self.chat_model = chat_model
        self.temperature = temperature
        self.system_instructions = system_instructions
        self.agent_name = agent_name
        self.full_response = full_response
        self.endpoint = f"{os.getenv('BACKEND_URL')}/api/messages"

    async def generate(self, model_input: ModelInput) -> Answer:
        """
        Sends the user's message and parameters to the backend API and returns an Answer.
        """
        payload = {
            "message": model_input.input,
            "model": self.chat_model,
            "system_instructions": self.system_instructions,
            "temperature": self.temperature,
            "agent_name": self.agent_name,
            "full_response": self.full_response,
        }
        try:
            response_text = ""
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(self.endpoint, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    response_text = data.get("content", None)

            except httpx.HTTPStatusError as http_err:
                raise RuntimeError(
                    f"API request failed with status {http_err.response.status_code}: {http_err.response.text}"
                ) from http_err
            except httpx.RequestError as req_err:
                raise RuntimeError(
                    f"An error occurred while requesting {req_err.request.url!r}: {req_err}"
                ) from req_err

        except Exception as e:
            logger.error(f"Error in AnswerGenerator: {e}")

        return Answer(
            output=response_text,
            input=model_input.input,
            references=model_input.references,
            subject=model_input.subject,
        )
