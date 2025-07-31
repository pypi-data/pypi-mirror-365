from deepeval.models.base_model import DeepEvalBaseLLM
from langchain_core.messages import SystemMessage, HumanMessage


class EvaluationModel(DeepEvalBaseLLM):
    """Wraps BaseChatModel in a format compatible with DeepEval"""

    def __init__(self, model, system_instruction: str = None):
        self.model = model
        self.system_instruction = system_instruction or "You are a helpful assistant."

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        messages = [
            SystemMessage(content=self.system_instruction),
            HumanMessage(content=prompt),
        ]
        return chat_model.invoke(messages).content

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        messages = [
            SystemMessage(content=self.system_instruction),
            HumanMessage(content=prompt),
        ]
        res = await chat_model.ainvoke(messages)
        return res.content

    def get_model_name(self):
        return "Evaluation Model"
