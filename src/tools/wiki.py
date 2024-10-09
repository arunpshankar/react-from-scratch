from src.config.logging import logger
from typing import Optional
import wikipediaapi
import json


def search(query: str) -> Optional[str]:
    """
    Fetch Wikipedia information for a given search query using Wikipedia-API and return as JSON.

    Args:
        query (str): The search query string.

    Returns:
        Optional[str]: A JSON string containing the query, title, and summary, or None if no result is found.
    """
    # Initialize Wikipedia API with a user agent
    wiki = wikipediaapi.Wikipedia(user_agent='ReAct Agents (shankar.arunp@gmail.com)',
                                  language='en')

    try:
        logger.info(f"Searching Wikipedia for: {query}")
        page = wiki.page(query)

        if page.exists():
            # Create a dictionary with query, title, and summary
            result = {
                "query": query,
                "title": page.title,
                "summary": page.summary
            }
            logger.info(f"Successfully retrieved summary for: {query}")
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            logger.info(f"No results found for query: {query}")
            return None

    except Exception as e:
        logger.exception(f"An error occurred while processing the Wikipedia query: {e}")
        return None


if __name__ == '__main__':
    queries = ["Geoffrey Hinton", "Demis Hassabis"]

    for query in queries:
        result = search(query)
        if result:
            print(f"JSON result for '{query}':\n{result}\n")
        else:
            print(f"No result found for '{query}'\n")