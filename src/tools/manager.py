from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.config.logging import logger
from pydantic import BaseModel
from typing import Callable
from typing import Union 
from typing import Dict 
from enum import Enum
from enum import auto 


ToolResult = Union[str, Exception]

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


class Tool:
    """
    Represents a tool with its execution function.
    """
    
    def __init__(self, name: ToolName, func: Callable[[str], ToolResult]):
        self.name = name
        self.func = func
    
    def act(self, query: str) -> ToolResult:
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
        self.tools: Dict[ToolName, Tool] = {}
    
    def register_tool(self, name: ToolName, func: Callable[[str], ToolResult]) -> None:
        """
        Register a new tool.
        """
        self.tools[name] = Tool(name, func)
    
    def execute_tool(self, tool_name: ToolName, query: str) -> ToolResult:
        """
        Execute a specific tool with the given query.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not registered")
        
        processed_query = query.split(' ', 1)[1] if ' ' in query else query
        return self.tools[tool_name].act(processed_query)
    
    def choose_tool(self, query: str) -> Choice:
        """
        Choose the appropriate tool based on the query prefix.
        """
        if query.startswith("/people"):
            return Choice(
                name=ToolName.WIKIPEDIA, 
                reason="Query starts with /people, using Wikipedia for biographical information."
            )
        elif query.startswith("/location"):
            return Choice(
                name=ToolName.GOOGLE, 
                reason="Query starts with /location, using Google for location-specific information."
            )
        else:
            raise ValueError("Unsupported query. Use /people or /location prefix.")


def run() -> None:
    """
    Run test cases for the ToolManager.
    """
    tool_manager = ToolManager()
    
    tool_manager.register_tool(ToolName.WIKIPEDIA, wiki_search)
    tool_manager.register_tool(ToolName.GOOGLE, google_search)
    
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
