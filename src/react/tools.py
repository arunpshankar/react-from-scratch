from src.config.logging import logger 
from typing import Optional
import requests


def wikipedia(q: str) -> Optional[str]:
    """
    Fetches a Wikipedia snippet for a given search query using Wikipedia's API.

    Args:
        q (str): The search query string.

    Returns:
        Optional[str]: The first search result's snippet from Wikipedia, or None if no result is found.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }

    try:
        logger.info(f"Sending request to Wikipedia API for query: {q}")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an exception for HTTP errors
        data = response.json()

        if "query" in data and data["query"]["search"]:
            snippet = data["query"]["search"][0]["snippet"]
            logger.info(f"Received snippet: {snippet}")
            return snippet
        else:
            logger.info(f"No results found for query: {q}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while making the request: {e}")
        return None
    except KeyError as e:
        logger.error(f"Unexpected response structure: {e}")
        return None


if __name__ == '__main__':
    # Examples of using the wikipedia function

    queries = ['Sachin Tendulkar', 'Python programming', 'Albert Einstein']
    
    for query in queries:
        logger.info(f"Fetching Wikipedia snippet for: {query}")
        result = wikipedia(query)
        
        if result:
            print(f"Snippet for '{query}': {result}\n")
        else:
            print(f"No snippet found for '{query}'\n")
