from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.config.logging import logger
from pydantic import BaseModel
from typing import Callable
from pydantic import Field 
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
    name: Name = Field(..., description="Name of the selected tool")
    reason: str = Field(..., description="Reason for selecting this tool")


class Tool:
    """
    Represents a tool with its execution function.
    """
    def __init__(self, name: Name, func: Callable[[str], str]):
        self.name = name
        self.func = func
    
    def use(self, query: str) -> Observation:
        """
        Execute the tool's function for a given query and handle exceptions.
        """
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return e


class Manager:
    """
    Manages tool registration, selection, and execution.
    """
    def __init__(self) -> None:
        self.tools: Dict[Name, Tool] = {} 
    
    def register(self, name: Name, func: Callable[[str], str]) -> None:
        """
        Register a new tool.
        """
        self.tools[name] = Tool(name, func)
    
    def act(self, name: Name, query: str) -> Observation:
        """
        Retrieve and use a registered tool to process the given query.

        Parameters:
            name (Name): The name of the tool to use.
            query (str): The input query string.

        Returns:
            Observation: The result of the tool's execution or an error.
        """
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        
        processed_query = query.split(' ', 1)[1] if ' ' in query else query
        return self.tools[name].use(processed_query)
    
    def choose(self, query: str) -> Choice:
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
    Initialize manager, register tools, and process test queries.
    """
    manager = Manager()
    
    manager.register(Name.WIKIPEDIA, wiki_search)
    manager.register(Name.GOOGLE, google_search)
    
    test_cases = [
    "/people kamala harris",
    "/location greek restaurants in miami",
    "What's the weather like today?",
    ]
    
    for i, query in enumerate(test_cases, 1):
        try:
            choice = manager.choose(query)
            result = manager.act(choice.name, query)
            
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