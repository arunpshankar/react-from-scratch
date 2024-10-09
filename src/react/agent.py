from vertexai.generative_models import GenerativeModel 
from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from vertexai.generative_models import Part 
from src.config.logging import logger
from src.config.setup import config
from src.llm.gemini import generate
from pydantic import BaseModel
from typing import Callable
from pydantic import Field 
from typing import Union
from typing import List 
from typing import Dict 
from enum import Enum
from enum import auto
import json


Observation = Union[str, Exception]

model = GenerativeModel(config.GEMINI_MODEL_NAME)

class Name(Enum):
    WIKIPEDIA = auto()
    GOOGLE = auto()
    NONE = auto()

    def __str__(self) -> str:
        return self.name.lower()


class Choice(BaseModel):
    name: Name = Field(..., description="The name of the tool chosen.")
    reason: str = Field(..., description="The reason for choosing this tool.")


class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender.")
    content: str = Field(..., description="The content of the message.")


class Tool:
    def __init__(self, name: Name, func: Callable[[str], str]):
        self.name = name
        self.func = func

    def use(self, query: str) -> Observation:
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return str(e)

class Agent:
    def __init__(self, model: GenerativeModel) -> None:
        self.model = model
        self.tools: Dict[Name, Tool] = {}
        self.messages: List[Message] = []
        self.query = ""
        self.max_iterations = 5
        self.current_iteration = 0
        self.output_file = f"./data/output/trace.txt"

    def register(self, name: Name, func: Callable[[str], str]) -> None:
        self.tools[name] = Tool(name, func)

    def trace(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        self.write_to_file(f"{role}: {content}\n")

    def write_to_file(self, content: str) -> None:
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(content)

    def get_history(self) -> str:
        return "\n".join([f"{message.role}: {message.content}" for message in self.messages])

    def think(self) -> None:
        self.current_iteration += 1
        logger.info(f"Starting iteration {self.current_iteration}")
        self.write_to_file(f"\n{'='*50}\nIteration {self.current_iteration}\n{'='*50}\n")

        if self.current_iteration > self.max_iterations:
            logger.warning("Reached maximum iterations. Stopping.")
            self.trace("assistant", "I'm sorry, but I couldn't find a satisfactory answer within the allowed number of iterations. Here's what I know so far: " + self.get_history())
            return

        prompt = f"""You are a ReAct (Reasoning and Acting) agent tasked with answering the following query:

Query: {self.query}

Your goal is to reason about the query and decide on the best course of action to answer it accurately.

Previous reasoning steps:
{self.get_history()}

Available tools:
{', '.join([str(tool.name) for tool in self.tools.values()])}

Instructions:
1. Analyze the query and previous reasoning steps.
2. Decide on the next action: use a tool or provide a final answer.
3. Respond in the following JSON format:

If you need to use a tool:
{{
    "thought": "Your detailed reasoning about what to do next",
    "action": {{
        "name": "Tool name (wikipedia, google, or none)",
        "reason": "Explanation of why you chose this tool"
    }}
}}

If you have enough information to answer the query:
{{
    "thought": "Your final reasoning process",
    "answer": "Your comprehensive answer to the query"
}}

Remember:
- Be thorough in your reasoning.
- Use tools when you need more information.
- Provide a final answer only when you're confident you have sufficient information.
"""

        self.trace("system", prompt)
        response = self.ask_gemini(prompt)
        logger.info(f"Thought: {response}")
        self.trace("assistant", response)
        self.process_response(response)

    def process_response(self, response: str) -> None:
        try:
            cleaned_response = response.strip().strip('`').strip()
            if cleaned_response.startswith('json'):
                cleaned_response = cleaned_response[4:].strip()
            
            parsed_response = json.loads(cleaned_response)
            
            if "action" in parsed_response:
                action = parsed_response["action"]
                tool_name = Name[action["name"].upper()]
                if tool_name == Name.NONE:
                    logger.info("No action needed. Proceeding to final answer.")
                    self.think()
                else:
                    self.act(tool_name, self.query)
            elif "answer" in parsed_response:
                self.trace("assistant", parsed_response["answer"])
            else:
                raise ValueError("Invalid response format")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {response}. Error: {str(e)}")
            self.trace("assistant", "I encountered an error in processing. Let me try again.")
            self.think()
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            self.trace("assistant", "I encountered an unexpected error. Let me try a different approach.")
            self.think()

    def act(self, tool_name: Name, query: str) -> None:
        tool = self.tools.get(tool_name)
        if tool:
            result = tool.use(query)
            self.trace("system", f"Observation: {result}")
            self.think()
        else:
            logger.error(f"No tool registered for choice: {tool_name}")
            self.trace("system", f"Error: Tool {tool_name} not found")
            self.think()

    def execute(self, query: str) -> str:
        self.query = query
        self.trace(role="user", content=query)
        self.think()
        return self.messages[-1].content

    def ask_gemini(self, prompt: str) -> str:
        contents = [Part.from_text(prompt)]
        response = generate(self.model, contents)
        return str(response) if response is not None else "No response from Gemini"

def run(query: str) -> str:
    gemini = GenerativeModel(config.GEMINI_MODEL_NAME)

    agent = Agent(model=gemini)
    agent.register(Name.WIKIPEDIA, wiki_search)
    agent.register(Name.GOOGLE, google_search)

    answer = agent.execute(query)
    logger.info(f"Final answer: {answer}")
    return answer

if __name__ == "__main__":
    query = 'who is older, kamala or tulsi gabbard'
    answer = run(query)
    logger.info(answer)