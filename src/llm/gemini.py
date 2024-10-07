from vertexai.generative_models import HarmBlockThreshold
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory
from vertexai.generative_models import Part
from src.config.logging import logger
from typing import Optional
from typing import Dict
from typing import List 
import json


def create_generation_config() -> GenerationConfig:
    """Creates and returns a generation configuration."""
    try:
        logger.info("Creating generation configuration")
        gen_config = GenerationConfig(
            temperature=0.0,
            top_p=1.0,
            candidate_count=1,
            max_output_tokens=8192,
            seed=12345
        )
        logger.info("Successfully created generation configuration")
        return gen_config
    except Exception as e:
        logger.error(f"Error creating generation configuration: {e}")
        raise


def create_safety_settings() -> Dict[HarmCategory, HarmBlockThreshold]:
    """Creates safety settings for content generation."""
    try:
        logger.info("Creating safety settings")
        safety_settings = {
            HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
        }
        logger.info("Successfully created safety settings")
        return safety_settings
    except Exception as e:
        logger.error(f"Error creating safety settings: {e}")
        raise


def generate(model: GenerativeModel, contents: List[Part]) -> Optional[str]:
    """
    Generates a response using the provided model and contents.
    
    Args:
        model (GenerativeModel): The generative model instance.
        contents (List[Part]): The list of content parts.
    
    Returns:
        Optional[str]: The generated response text, or None if an error occurs.
    """
    try:
        logger.info("Generating response from model")
        response = model.generate_content(
            contents,
            generation_config=create_generation_config(),
            safety_settings=create_safety_settings()
        )

        if not response.text:
            logger.error("Empty response from the model")
            return None

        logger.info("Successfully generated response")
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None