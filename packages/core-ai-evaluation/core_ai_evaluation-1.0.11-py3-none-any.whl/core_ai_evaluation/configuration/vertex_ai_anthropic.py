import os

from langchain_google_vertexai.model_garden import ChatAnthropicVertex

from core_ai_evaluation.configuration.provider import ModelFeatures, ModelProvider


class VertexAIAnthropicProvider(ModelProvider):
    def get_chat_model(
        self,
        model_name: str,
        temperature: float,
        top_k: int = None,
        top_p: float = None,
        **kwargs,
    ) -> ChatAnthropicVertex:
        location = os.getenv("VERTEX_AI_LOCATION") or "europe-west1"

        return ChatAnthropicVertex(
            model=model_name,
            location=location,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            temperature=temperature if temperature <= 1 else 1,
            top_k=top_k,
            top_p=top_p,
            max_retries=2,
            streaming=True,
            **kwargs,
        )

    def return_required_env_vars(self) -> list[str]:
        return [
            "GOOGLE_CLOUD_PROJECT",
        ]

    @property
    def features(self) -> set[ModelFeatures]:
        return {
            ModelFeatures.TOOL_CALLING,
            ModelFeatures.FILE_UPLOAD,
            ModelFeatures.STRUCTURED_OUTPUT,
        }

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
