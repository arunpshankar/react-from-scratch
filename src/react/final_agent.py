from vertexai.generative_models import GenerativeModel
from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.config.logging import logger
from src.config.setup import config
from pydantic import BaseModel, Field
from typing import Callable, Union, Dict
from enum import Enum, auto


Observation = Union[str, Exception]


class Name(Enum):
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
    name: Name = Field(..., description="The name of the tool chosen.")
    reason: str = Field(..., description="The reason for choosing this tool.")


class Message(BaseModel):
    """
    Represents a message exchanged within the agent.
    """
    role: str = Field(..., description="The role of the message sender.")
    content: str = Field(..., description="The content of the message.")


class Tool:
    """
    Represents a tool with its execution function.
    """
    def __init__(self, name: Name, func: Callable[[str], str]):
        self.name = name
        self.func = func

    def use(self, query: str) -> Observation:
        """
        Execute the tool's function and handle exceptions.
        """
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return e


class Agent:
    """
    An agent that manages tools and processes queries.
    """
    def __init__(self, model: GenerativeModel) -> None:
        self.model = model
        self.tools: Dict[Name, Tool] = {}
        self.messages: list[Message] = []

    def register_tool(self, name: Name, func: Callable[[str], str]) -> None:
        """
        Register a new tool.
        """
        self.tools[name] = Tool(name, func)

    def append_message(self, role: str, content: str) -> None:
        """
        Append a new message to the message history.
        """
        self.messages.append(Message(role=role, content=content))

    def think(self, query: str) -> Choice:
        """
        Decide which tool to use based on the query.
        """
        # Simplified example decision logic
        if "who" in query:
            choice = Choice(name=Name.WIKIPEDIA, reason="Query is informational.")
        else:
            choice = Choice(name=Name.GOOGLE, reason="General search is needed.")
        return choice

    def act(self, query: str) -> Observation:
        """
        Execute the chosen tool based on the query.
        """
        choice = self.think(query)
        tool = self.tools.get(choice.name)
        if tool:
            return tool.use(query)
        logger.error(f"No tool registered for choice: {choice.name}")
        return Exception("Tool not found")

    def execute(self, query: str) -> str:
        """
        Process the query end-to-end by choosing, acting, and observing results.
        """
        self.append_message(role="user", content=query)
        result = self.act(query)
        response = str(result) if isinstance(result, str) else "An error occurred."
        self.append_message(role="agent", content=response)
        return response


def run(query: str) -> str:
    gemini = GenerativeModel(config.GEMINI_MODEL_NAME)

    # Create and set up ReAct agent
    agent = Agent(model=gemini)
    agent.register_tool(Name.WIKIPEDIA, wiki_search)
    agent.register_tool(Name.GOOGLE, google_search)

    answer = agent.execute(query)
    return answer


if __name__ == "__main__":
    query = 'Who is Sachin Tendulkar and what is his connection to tennis?'
    answer = run(query)
    logger.info(answer)
