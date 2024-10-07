import re
import logging
from src.llm.gemini import generate, create_generation_config, create_safety_settings 
from src.tools.wiki import search as wiki_search
from src.tools.serp import search as google_search
from typing import Callable, Dict, List
from vertexai.generative_models import GenerativeModel, Part

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, name: str, function: Callable[[str], str]):
        self.name = name
        self.function = function

    def act(self, input_data: str) -> str:
        try:
            result = self.function(input_data)
            logger.info(f"Tool '{self.name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{self.name}': {e}")
            raise

class ReActAgent:
    def __init__(self, system: str, model: GenerativeModel):
        self.system = system
        self.model = model
        self.messages = []
        self.tools = {}
        if self.system:
            self.messages.append({"role": "system", "content": self.system})

    def add_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool
        logger.info(f"Tool '{tool.name}' added to the agent.")

    def __call__(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self) -> str:
        try:
            contents = [Part.from_text(msg["content"]) for msg in self.messages]
            generation_config = create_generation_config()
            safety_settings = create_safety_settings()
            
            response = generate(self.model, contents)
            
            if response:
                logger.info("Gemini model executed successfully.")
                return response.get("content", "")
            else:
                logger.error("Error: Empty response from Gemini model.")
                return "Error: Unable to generate a response."
        except Exception as e:
            logger.error(f"Error executing Gemini model: {e}")
            raise

def wikipedia(q: str) -> str:
    try:
        result = wiki_search(q)
        logger.info(f"Wikipedia search for '{q}' completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Error during Wikipedia search for '{q}': {e}")
        raise

def google_search(q: str) -> str:
    try:
        result = google_search(q)
        logger.info(f"Google search for '{q}' completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Error during Google search for '{q}': {e}")
        raise

# Define tools
wikipedia_tool = Tool(name="wikipedia", function=wikipedia)
google_search_tool = Tool(name="google_search", function=google_search)

# Initialize agent and add tools
prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

google_search:
e.g. google_search: Django
Performs a Google search for the term

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
"""

# Initialize the Gemini model
gemini_model = GenerativeModel("gemini-pro")

react_agent = ReActAgent(system=prompt, model=gemini_model)
react_agent.add_tool(wikipedia_tool)
react_agent.add_tool(google_search_tool)

action_re = re.compile(r'^Action: (\w+): (.*)$')

def query(question: str, max_turns: int = 5) -> None:
    i = 0
    agent = react_agent
    next_prompt = question
    while i < max_turns:
        i += 1
        try:
            result = agent(next_prompt)
            logger.info(f"Agent response: {result}")
            print(result)
            actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
            if actions:
                action, action_input = actions[0].groups()
                if action not in agent.tools:
                    logger.error(f"Unknown action: {action}: {action_input}")
                    raise ValueError(f"Unknown action: {action}: {action_input}")
                logger.info(f"Running action '{action}' with input '{action_input}'")
                observation = agent.tools[action].act(action_input)
                logger.info(f"Observation: {observation}")
                print("Observation:", observation)
                next_prompt = f"Observation: {observation}"
            else:
                return
        except Exception as e:
            logger.error(f"Error during query processing: {e}")
            break

if __name__ == "__main__":
    sample_question = "What is the capital of France?"
    query(sample_question)