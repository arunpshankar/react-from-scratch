from src.config.logging import logger
from typing import Optional
from typing import Dict 
from typing import Any 
import json 
import yaml


def read_file(path: str) -> Optional[str]:
    """
    Reads the content of a markdown file and returns it as a text object.

    Args:
        path (str): The path to the markdown file.

    Returns:
        Optional[str]: The content of the file as a string, or None if the file could not be read.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content: str = file.read()
        return content
    except FileNotFoundError:
        logger.info(f"File not found: {path}")
        return None
    except Exception as e:
        logger.info(f"Error reading file: {e}")
        return None


def load_yaml(filename: str) -> Dict[str, Any]:
    """
    Load a YAML file and return its contents.

    Args:
        filename (str): The path to the YAML file.

    Returns:
        Dict[str, Any]: The parsed YAML object.

    Raises:
        FileNotFoundError: If the file is not found.
        yaml.YAMLError: If there is an error parsing the YAML file.
        Exception: For any other exceptions.
    """
    try:
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"File '{filename}' not found.")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file '{filename}': {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading YAML file: {e}")
        raise


def load_json(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load a JSON file and return its contents.

    Args:
        filename (str): The path to the JSON file.

    Returns:
        Optional[Dict[str, Any]]: The parsed JSON object, or None if an error occurs.

    Raises:
        FileNotFoundError: If the file is not found.
        json.JSONDecodeError: If there is an error parsing the JSON file.
        Exception: For any other exceptions.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        logger.error(f"File '{filename}' contains invalid JSON.")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise


def write_to_file(path: str, content: str) -> None:
    """
    Writes content to a specified file. Appends to the file if it already exists.

    Args:
        path (str): The path to the file.
        content (str): The content to write to the file.

    Raises:
        Exception: For any other exceptions encountered during file writing.
    """
    try:
        with open(path, 'a', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"Content written to file: {path}")
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Error writing to file '{path}': {e}")
        raise
