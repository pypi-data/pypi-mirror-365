import os

from langchain_google_vertexai import ChatVertexAI

from core_ai_evaluation.configuration.provider import ModelFeatures, ModelProvider


class GeminiProvider(ModelProvider):
    def get_chat_model(
        self,
        model_name: str,
        temperature: float,
        top_k: int = None,
        top_p: float = None,
        **kwargs,
    ) -> ChatVertexAI:
        # exp models are only available in us-central1
        location = (
            "us-central1"
            if "exp" in model_name or "preview" in model_name
            else os.getenv("VERTEX_AI_LOCATION") or "europe-west1"
        )

        return ChatVertexAI(
            model=model_name,
            location=location,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_retries=2,
            streaming=True,
            **kwargs,
        )

    def supports(self, feature: ModelFeatures, model_name: str = ""):
        if model_name == "gemini-2.0-flash-thinking-exp-01-21":
            return None
        return super().supports(feature, model_name)

    @property
    def features(self) -> set[ModelFeatures]:
        return {
            ModelFeatures.TOOL_CALLING,
            ModelFeatures.FILE_UPLOAD,
            ModelFeatures.STRUCTURED_OUTPUT,
        }

    def return_required_env_vars(self) -> list[str]:
        return [
            "GOOGLE_CLOUD_PROJECT",
        ]

    @property
    def requirements_met(self) -> bool:
        return os.getenv("GOOGLE_CLOUD_PROJECT") is not None

    @property
    def supported_mime_types(self) -> set[str]:
        return {
            "application/pdf",
            "audio/mpeg",
            "audio/mp3",
            "audio/wav",
            "image/png",
            "image/jpeg",
            "image/webp",
            "text/plain",
            "video/mov",
            "video/mpeg",
            "video/mp4",
            "video/mpg",
            "video/avi",
            "video/wmv",
            "video/mpegps",
            "video/flv",
        }
