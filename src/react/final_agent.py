from vertexai.generative_models import GenerativeModel
from src.config.logging import logger 
from src.config.setup import config
from src.llm.gemini import generate
from pydantic import BaseModel
from pydantic import Field 
from enum import Enum
from enum import auto 


model = GenerativeModel(config.GEMINI_MODEL_NAME)

class Tool(Enum):
    WIKIPEDIA = auto()
    GOOGLE = auto()

    def __str__(self):
        return self.name.lower()


class Choice(BaseModel):
    name: Tool = Field(..., description="The name of the chosen tool")
    reason: str = Field(..., description="The reason for choosing this tool")


class Tool:
    def __init__(self, name: ToolName, func: Callable[[str], str]) -> None:
        self.name = name
        self.func = func

    def act(self, query: str) -> str:
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return f"Error: {str(e)}"




print(Tool.GOOGLE)


if __name__ == '__main__':
    pass