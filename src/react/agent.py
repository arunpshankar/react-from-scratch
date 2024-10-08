from vertexai.generative_models import GenerativeModel
from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from vertexai.generative_models import Part 
from src.config.logging import logger
from src.llm.gemini import generate
from src.config.setup import config
from dataclasses import dataclass
from typing import Callable
from typing import List 
from typing import Dict 
import re


@dataclass
class Tool:
    """
    Represents a tool that can be used by the ReAct agent.
    """
    name: str
    function: Callable[[str], str]
    description: str

    def act(self, input_data: str) -> str:
        """
        Execute the tool's function with the given input.

        Args:
            input_data (str): The input data for the tool.

        Returns:
            str: The result of the tool's execution.

        Raises:
            Exception: If there's an error during tool execution.
        """
        try:
            result = self.function(input_data)
            logger.info(f"Tool '{self.name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{self.name}': {e}")
            raise

class ReActAgent:
    """
    A ReAct (Reason+Act) agent that uses tools to answer questions.

    This module implements a ReAct agent that uses Wikipedia and Google Search
    as tools to answer questions. The agent follows a loop of Thought, Action, and Observation
    to generate responses to user queries.

    The agent prioritizes Wikipedia searches and falls back to Google Search when necessary.
    It can also combine information from both sources to provide comprehensive answers.
    """

    def __init__(self, model: GenerativeModel):
        """
        Initialize the ReActAgent.

        Args:
            model (GenerativeModel): The generative model to use for reasoning.
        """
        self.model = model
        self.tools: Dict[str, Tool] = {}
        self.messages: List[Dict[str, str]] = []
        self._initialize_system_prompt()

    def _initialize_system_prompt(self):
        """
        Initialize the system prompt for the agent.
        """
        prompt = """
        You are an AI assistant that follows a loop of Thought, Action, PAUSE, and Observation to answer questions.
        At the end of the loop, you output an Answer.

        Use Thought to describe your reasoning about the question.
        Use Action to run one of the available tools, then return PAUSE.
        Observation will be the result of running those actions.

        Your available actions are:

        wikipedia:
        e.g. wikipedia: Django
        Returns a summary from searching Wikipedia

        google_search:
        e.g. google_search: Django web framework
        Performs a Google search and returns relevant information

        Follow these guidelines:
        1. Always start with a Wikipedia search for factual queries.
        2. If Wikipedia doesn't provide a complete answer, use Google Search for additional information.
        3. If you find partial information on Wikipedia, use both Wikipedia and Google Search to complete the answer.
        4. If Wikipedia doesn't have relevant information, rely on Google Search.
        5. Combine information from both sources when necessary to provide comprehensive answers.

        Example session:

        Human: What is the capital of France, and what's a famous landmark there?
        Thought: I should start by looking up France on Wikipedia to find its capital and possibly a famous landmark.
        Action: wikipedia: France
        PAUSE

        Observation: France is a country in Western Europe. The capital and largest city is Paris. Paris is known for many landmarks, including the Eiffel Tower.

        Thought: I've found the capital of France (Paris) and a famous landmark (Eiffel Tower) from Wikipedia. To provide more detailed information about the Eiffel Tower, I'll use Google Search.
        Action: google_search: Eiffel Tower famous landmark Paris
        PAUSE

        Observation: The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889 as the entrance arch to the 1889 World's Fair, it was initially criticized by some of France's leading artists and intellectuals for its design, but it has become a global cultural icon of France and one of the most recognizable structures in the world.

        Answer: The capital of France is Paris. A famous landmark in Paris is the Eiffel Tower. The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars. It was constructed between 1887 and 1889 as the entrance arch to the 1889 World's Fair. Despite initial criticism, it has become a global cultural icon of France and one of the most recognizable structures worldwide. The tower is named after Gustave Eiffel, whose company designed and built it.
        """
        self.messages.append({"role": "system", "content": prompt})

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the agent's toolset.

        Args:
            tool (Tool): The tool to add.
        """
        self.tools[tool.name] = tool
        logger.info(f"Tool '{tool.name}' added to the agent.")

    def execute(self, question: str, max_turns: int = 3) -> str:
        """
        execute a query using the ReAct agent.

        Args:
            question (str): The question to be answered.
            max_turns (int, optional): Maximum number of turns for the agent. Defaults to 5.

        Returns:
            str: The final answer generated by the agent.

        Raises:
            Exception: If there's an error during query processing.
        """
        self.messages.append({"role": "user", "content": question})
        
        for _ in range(max_turns):
            try:
                response = self._generate_response()
                logger.info(f"Agent response: {response}")

                if response.lower().startswith("answer:"):
                    return response

                action_match = re.search(r'^Action: (\w+): (.*)$', response, re.MULTILINE)
                if action_match:
                    action, action_input = action_match.groups()
                    if action not in self.tools:
                        raise ValueError(f"Unknown action: {action}")
                    
                    observation = self.tools[action].act(action_input)
                    logger.info(f"Observation: {observation}")
                    self.messages.append({"role": "system", "content": f"Observation: {observation}"})
                else:
                    logger.warning("No action found in the response.")
            except Exception as e:
                logger.error(f"Error during query processing: {e}")
                return f"An error occurred while processing your query: {str(e)}"

        return "I apologize, but I couldn't find a definitive answer within the allowed number of turns."

    def _generate_response(self) -> str:
        """
        Generate a response using the Gemini model.

        Returns:
            str: The generated response.

        Raises:
            Exception: If there's an error in generating the response.
        """
        try:
            contents = [Part.from_text(message["content"]) for message in self.messages]
            print('>' * 10)
            print(contents)
            print('++' * 10)
            response = generate(self.model, contents)
            if response:
                logger.info("Gemini model executed successfully.")
                return response
            else:
                raise ValueError("Empty response from Gemini model.")
        except Exception as e:
            logger.error(f"Error executing Gemini model: {e}")
            raise

def run():
    """
    afddadfda
    """
    # Initialize the Gemini model
    gemini_model = GenerativeModel(config.GEMINI_MODEL_NAME)

    # Create and set up the ReActAgent
    agent = ReActAgent(model=gemini_model)
    agent.add_tool(Tool(name="wikipedia", function=wiki_search, description="Search Wikipedia for information"))
    agent.add_tool(Tool(name="google_search", function=google_search, description="Perform a Google search"))

    # Example queries to demonstrate different scenarios
    queries = [
        "What is the capital of Italy, and what's a famous landmark there?"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.execute(query)
        print(f"Final Answer: {response}\n")
        print("-" * 50)

if __name__ == "__main__":
    run()