from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.config.logging import logger
from pydantic import BaseModel
from typing import Callable
from typing import Union 
from typing import Dict 
from enum import Enum
from enum import auto 


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
    name: Name
    reason: str


class Tool:
    """
    Represents a tool with its execution function.
    """
    
    def __init__(self, name: Name, func: Callable[[str]]):
        self.name = name
        self.func = func
    
    def use(self, query: str) -> Observation:
        """Execute the tool's function and handle exceptions."""
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return e


class ToolManager:
    """
    Manages tool registration, selection, and execution.
    """
    
    def __init__(self) -> None:
        self.tools: Dict[Name, Tool] = {}
    
    def register_tool(self, name: Name, func: Callable[[str]]) -> None:
        """
        Register a new tool.
        """
        self.tools[name] = Tool(name, func)
    
    def execute_tool(self, name: Name, query: str) -> Observation:
        """
        Execute a specific tool with the given query.
        """
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        
        processed_query = query.split(' ', 1)[1] if ' ' in query else query
        return self.tools[name].act(processed_query)
    
    def choose_tool(self, query: str) -> Choice:
        """
        Choose the appropriate tool based on the query prefix.
        """
        if query.startswith("/people"):
            return Choice(
                name=Name.WIKIPEDIA, 
                reason="Query starts with /people, using Wikipedia for biographical information."
            )
        elif query.startswith("/location"):
            return Choice(
                name=Name.GOOGLE, 
                reason="Query starts with /location, using Google for location-specific information."
            )
        else:
            raise ValueError("Unsupported query. Use /people or /location prefix.")


def run() -> None:
    """
    Run test cases for the ToolManager.
    """
    tool_manager = ToolManager()
    
    tool_manager.register_tool(Name.WIKIPEDIA, wiki_search)
    tool_manager.register_tool(Name.GOOGLE, google_search)
    
    test_cases = [
        "/people kamala harris",
        "/location greek restaurants in miami",
        "What's the weather like today?",
    ]
    
    for i, query in enumerate(test_cases, 1):
        try:
            choice = tool_manager.choose_tool(query)
            result = tool_manager.execute_tool(choice.name, query)
            
            logger.info(f"Test Case {i}:")
            logger.info(f"Query: {query}")
            logger.info(f"Tool used: {choice.name}")
            logger.info(f"Reason: {choice.reason}")
            logger.info(f"Result: {result}")
        except ValueError as e:
            logger.error(f"Test Case {i}:")
            logger.error(f"Query: {query}")
            logger.error(f"Error: {str(e)}")
        logger.info("")  # Empty line for readability


if __name__ == "__main__":
    run()
