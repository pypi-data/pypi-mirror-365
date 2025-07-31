import os

from langchain_ollama import ChatOllama

from core_ai_evaluation.configuration.provider import ModelFeatures, ModelProvider


class OllamaProvider(ModelProvider):
    def get_chat_model(
        self,
        model_name: str,
        temperature: float,
        top_k: int = None,
        top_p: float = None,
        **kwargs,
    ) -> ChatOllama:
        return ChatOllama(
            model=model_name,
            base_url=os.getenv("OLLAMA_BASE_URL"),
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            **kwargs,
        )

    def supports(self, feature: ModelFeatures, model_name: str = "") -> bool:
        if model_name == "gemma2:2b":
            # apparently gemma2:2d does not support anything besides text
            return False
        return feature in self.features

    def return_required_env_vars(self) -> list[str]:
        return ["OLLAMA_BASE_URL"]

    @property
    def requirements_met(self) -> bool:
        return os.getenv("OLLAMA_BASE_URL") is not None

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
