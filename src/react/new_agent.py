from __future__ import annotations

import logging
import json
from typing import Callable, List, Dict, Optional, Union
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerativeModel, Part
from enum import Enum
from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.llm.gemini import generate
from src.config.setup import config


class ToolName(str, Enum):
    WIKIPEDIA = "WikipediaSearch"
    GOOGLE = "GoogleSearch"

class ReactEnd(BaseModel):
    stop: bool = Field(..., description="Whether to stop the reasoning process")
    final_answer: str = Field(..., description="The final answer to the query")

class ToolChoice(BaseModel):
    tool_name: ToolName = Field(..., description="The name of the chosen tool")
    reason_of_choice: str = Field(..., description="The reason for choosing this tool")

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

class Message(BaseModel):
    role: str
    content: str

class Agent:
    def __init__(self, model: GenerativeModel) -> None:
        self.model = model
        self.tools: Dict[ToolName, Tool] = {}
        self.messages: List[Message] = []
        self.request: str = ""

    def add_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool
        logger.info(f"Added tool: {tool.name}")

    def append_message(self, role: str, content: str) -> None:
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.token_count += len(content)

        while self.token_count > self.token_limit and len(self.messages) > 1:
            removed_message = self.messages.pop(1)
            self.token_count -= len(removed_message.content)

    def background_info(self) -> str:
        return "\n".join([f"{msg.role}: {msg.content}" for msg in self.messages[1:]])

    def generate_content(self, prompt: str, output_class: Optional[BaseModel] = None) -> Union[str, BaseModel]:
        try:
            contents = [Part.from_text(prompt)]
            response = generate(self.model, contents)
            
            if output_class:
                try:
                    # Try to parse the response as JSON
                    json_response = json.loads(response)
                    return output_class(**json_response)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract relevant information from the text
                    if output_class == ToolChoice:
                        for tool_name in ToolName:
                            if tool_name.value.lower() in response.lower():
                                return ToolChoice(
                                    tool_name=tool_name,
                                    reason_of_choice=f"Extracted from response: {response[:100]}..."
                                )
                        # If no tool name is found, default to Wikipedia
                        return ToolChoice(
                            tool_name=ToolName.WIKIPEDIA,
                            reason_of_choice="Default choice due to parsing error."
                        )
                    elif output_class == ReactEnd:
                        stop = "final answer" in response.lower() or "enough information" in response.lower()
                        return ReactEnd(
                            stop=stop,
                            final_answer=response if stop else "Not enough information yet."
                        )
            return response
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def think(self) -> None:
        prompt = f"""Answer the following request as best you can: {self.request}.
                    Previous context:
                    {self.background_info()}
                    First, think about what to do. What action to take first, if any.
                    Available tools: {', '.join([tool.name for tool in self.tools.values()])}"""

        self.append_message("system", prompt)
        response = self.generate_content(prompt)
        logger.info(f"Thought: {response}")
        self.append_message("assistant", response)
        self.choose_action()

    def choose_action(self) -> None:
        prompt = f"""To answer the following request as best you can: {self.request}.
                    Previous context:
                    {self.background_info()}
                    Choose the most appropriate tool to use. Available tools:
                    {', '.join([tool.name for tool in self.tools.values()])}.
                    Respond with a JSON object containing 'tool_name' and 'reason_of_choice'.
                    """
        self.append_message("system", prompt)
        tool_choice: ToolChoice = self.generate_content(prompt, ToolChoice)

        logger.info(f"Action: Using tool: {tool_choice.tool_name}. Reason: {tool_choice.reason_of_choice}")
        self.append_message("assistant", f"Action: {tool_choice.tool_name}")

        tool = self.tools[tool_choice.tool_name]
        self.action(tool)

    def action(self, tool: Tool) -> None:
        prompt = f"""To answer the following request as best you can: {self.request}.
                    Previous context:
                    {self.background_info()}
                    Determine the specific query to send to the tool: {tool.name}
                    """
        self.append_message("system", prompt)
        query = self.generate_content(prompt)
        self.append_message("assistant", f"Query: {query}")

        action_result = tool.act(query)
        logger.info(f"Action result: {action_result}")
        self.append_message("system", f"Results of action: {action_result}")
        self.observation()

    def observation(self) -> None:
        prompt = f"""Based on the previous actions and results, what can we conclude? 
                     Is this enough to answer the original request: {self.request}?
                     Respond with a JSON object containing 'stop' (boolean) and 'final_answer' (string).
                     """
        self.append_message("system", prompt)

        check_final: ReactEnd = self.generate_content(prompt, ReactEnd)

        if check_final.stop:
            logger.info("Final answer reached.")
            final_answer = check_final.final_answer
            logger.info(f"Final Answer: {final_answer}")
            self.append_message("assistant", f"Final Answer: {final_answer}")
        else:
            logger.info("Continuing the reasoning process.")
            self.think()

    def react(self, input: str) -> str:
        self.request = input
        self.append_message("user", input)
        self.think()
        return self.messages[-1].content

def main():
    # Initialize the Gemini model
    gemini_model = GenerativeModel(config.GEMINI_MODEL_NAME)

    # Create and set up the ReActAgent
    agent = Agent(model=gemini_model)
    agent.add_tool(Tool(ToolName.WIKIPEDIA, wiki_search))
    agent.add_tool(Tool(ToolName.GOOGLE, google_search))

    query = "What is the capital of France and what's a famous landmark that was constructed in 2020?"
    result = agent.react(query)
    print(f"Query: {query}")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()