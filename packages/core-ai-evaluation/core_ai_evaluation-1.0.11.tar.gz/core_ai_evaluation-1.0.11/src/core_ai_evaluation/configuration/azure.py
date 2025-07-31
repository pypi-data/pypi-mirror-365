import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from core_ai_evaluation.configuration.provider import ModelFeatures, ModelProvider


class AzureOpenAIProvider(ModelProvider):
    def get_chat_model(
        self,
        model_name: str,
        temperature: float,
        top_k: int = None,
        top_p: float = None,
        **kwargs,
    ) -> BaseChatModel:
        return AzureChatOpenAI(
            azure_deployment=model_name,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION") or "2025-01-01-preview",
            model=model_name,
            max_retries=2,
            temperature=temperature,
            top_p=top_p,
            streaming=True,
            **kwargs,
        )

    def return_required_env_vars(self) -> list[str]:
        return [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
        ]

    @property
    def requirements_met(self) -> bool:
        return (
            os.getenv("AZURE_OPENAI_API_KEY") is not None
            and os.getenv("AZURE_OPENAI_ENDPOINT") is not None
        )

    @property
    def features(self) -> set[ModelFeatures]:
        return {
            ModelFeatures.TOOL_CALLING,
            ModelFeatures.FILE_UPLOAD,
            ModelFeatures.STRUCTURED_OUTPUT,
        }

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
