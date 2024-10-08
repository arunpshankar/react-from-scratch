from vertexai.generative_models import GenerativeModel
from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.config.logging import logger
from src.config.setup import config
from pydantic import BaseModel
from typing import Callable
from pydantic import Field 
from typing import Union 
from typing import Dict 
from enum import Enum
from enum import auto 

class ToolName(Enum):
    """
    Enumeration of available tools.
    """
    WIKIPEDIA = auto()
    GOOGLE = auto()

    def __str__(self) -> str:
        return self.name.lower()


class Choice(BaseModel):
    """
    Represents a tool choice with a reason.
    """
    name: ToolName
    reason: str


class Message(BaseModel):
    role: str
    content: str


class Tool:
    """
    Represents a tool with its execution function.
    """
    
    def __init__(self, name: ToolName, func: Callable[[str], ToolResult]):
        self.name = name
        self.func = func
    
    def act(self, query: str) -> ToolResult:
        """
        Execute the tool's function and handle exceptions.
        """
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return e


class Agent:
    def __init__(self, model: GenerativeModel) -> None:
        self.model = model
        self.tools = None 
        self.messages = None 

    def register_tool():
        pass

    def append_message():
        pass

    def think():
        pass

    def choose():
        pass

    def act():
        pass

    def observe():
        pass 

    def execute():
        pass

def run(query: str) -> str:
    gemini = GenerativeModel(config.GEMINI_MODEL_NAME)

    # create and setup ReAct agent 
    agent = Agent(model=gemini)
    agent.register_tool()
    agent.register_tool()

    ans = agent.execute(query)
    return ans 




if __name__ == "__main__":
    query = 'who is sachin tendulkar and what is his connection to tennis?'
    ans = run(query) 
    logger.info(ans)