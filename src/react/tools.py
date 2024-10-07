from src.config.logging import logger
from typing import Optional
import wikipediaapi


def wikipedia(query: str) -> Optional[str]:
    """
    Fetch a Wikipedia paragraph for a given search query using Wikipedia-API.

    Args:
        query (str): The search query string.

    Returns:
        Optional[str]: A paragraph built from the first search result, or None if no result is found.
    """
    # Initialize Wikipedia API with a user agent
    wiki = wikipediaapi.Wikipedia(user_agent='ReAct Agents (shankar.arunp@gmail.com)', 
                                  language='en')

    try:
        logger.info(f"Searching Wikipedia for: {query}")
        page = wiki.page(query)

        if page.exists():
            # Build a paragraph from the page summary
            paragraph = f"{page.title}: {page.summary[:100]}..."
            logger.info(f"Successfully retrieved summary for: {query}")
            return paragraph
        else:
            logger.info(f"No results found for query: {query}")
            return None

    except Exception as e:
        logger.exception(f"An error occurred while processing the Wikipedia query: {e}")
        return None

if __name__ == '__main__':
    queries = ['Sachin Tendulkar', 'Albert Einstein']

    for query in queries:
        result = wikipedia(query)
        if result:
            print(f"Paragraph for '{query}': {result}\n")
        else:
            print(f"No paragraph found for '{query}'\n")