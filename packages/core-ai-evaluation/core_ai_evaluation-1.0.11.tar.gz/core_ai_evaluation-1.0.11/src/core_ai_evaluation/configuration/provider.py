from abc import ABC
from enum import Enum, auto

from langchain_core.language_models import BaseChatModel


class ModelFeatures(Enum):
    FILE_UPLOAD = auto()
    TOOL_CALLING = auto()
    STRUCTURED_OUTPUT = auto()


class ModelProvider(ABC):
    def get_chat_model(
        self,
        model_name: str,
        temperature: float,
        **kwargs,
    ) -> BaseChatModel:
        raise NotImplementedError

    def supports(self, feature: ModelFeatures, model_name: str = ""):
        return self.features is not None and feature in self.features

    def supports_mime_type(self, mime_type: str, model_name: str = ""):
        return (
            self.supported_mime_types is not None
            and mime_type in self.supported_mime_types
        )

    def fix_mime_type(self, mime_type: str, model_name: str) -> str:
        if self.supports_mime_type(mime_type, model_name):
            return mime_type
        # don't know why some pdfs have this mime type
        if mime_type == "pdf":
            return "application/pdf"
        return None

    def return_required_env_vars(self) -> list[str]:
        raise NotImplementedError

    @property
    def requirements_met(self) -> bool:
        raise NotImplementedError

    @property
    def default_model(self) -> str:
        raise NotImplementedError

    @property
    def features(self) -> set[ModelFeatures]:
        raise NotImplementedError

    @property
    def supported_mime_types(self) -> set[str]:
        raise NotImplementedError
