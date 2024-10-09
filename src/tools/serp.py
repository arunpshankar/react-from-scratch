from src.config.logging import logger
from src.utils.io import load_yaml
from typing import Tuple
from typing import Union
from typing import Dict
from typing import List
from typing import Any 
import requests
import json


# Static paths
CREDENTIALS_PATH = './credentials/key.yml'

class SerpAPIClient:
    """
    A client for interacting with the SERP API for performing search queries.
    """

    def __init__(self, api_key: str):
        """
        Initialize the SerpAPIClient with the provided API key.

        Parameters:
        -----------
        api_key : str
            The API key for authenticating with the SERP API.
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"

    def __call__(self, query: str, engine: str = "google", location: str = "") -> Union[Dict[str, Any], Tuple[int, str]]:
        """
        Perform Google search using the SERP API.

        Parameters:
        -----------
        query : str
            The search query string.
        engine : str, optional
            The search engine to use (default is "google").
        location : str, optional
            The location for the search query (default is an empty string).

        Returns:
        --------
        Union[Dict[str, Any], Tuple[int, str]]
            The search results as a JSON dictionary if successful, or a tuple containing the HTTP status code
            and error message if the request fails.
        """
        params = {
            "engine": engine,
            "q": query,
            "api_key": self.api_key,
            "location": location
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to SERP API failed: {e}")
            return response.status_code, str(e)


def load_api_key(credentials_path: str) -> str:
    """
    Load the API key from the specified YAML file.

    Parameters:
    -----------
    credentials_path : str
        The path to the YAML file containing the API credentials.

    Returns:
    --------
    str
        The API key extracted from the YAML file.

    Raises:
    -------
    KeyError
        If the 'serp' or 'key' keys are missing in the YAML file.
    """
    config = load_yaml(credentials_path)
    return config['serp']['key']


def format_top_search_results(results: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Format the top N search results into a list of dictionaries with updated key names.

    Parameters:
    -----------
    results : Dict[str, Any]
        The search results returned from the SERP API.
    top_n : int, optional
        The number of top search results to format (default is 10).

    Returns:
    --------
    List[Dict[str, Any]]
        A list of dictionaries containing the formatted top search results with updated key names.
    """
    return [
        {
            "position": result.get('position'),
            "title": result.get('title'),
            "link": result.get('link'),
            "snippet": result.get('snippet')
        }
        for result in results.get('organic_results', [])[:top_n]
    ]


def search(search_query: str, location: str = "") -> str:
    """
    Main function to execute the Google search using SERP API and return the top results as a JSON string.

    Parameters:
    -----------
    search_query : str
        The search query to be executed using the SERP API.
    location : str, optional
        The location to include in the search query (default is an empty string).

    Returns:
    --------
    str
        A JSON string containing the top search results or an error message, with updated key names.
    """
    # Load the API key
    api_key = load_api_key(CREDENTIALS_PATH)

    # Initialize the SERP API client
    serp_client = SerpAPIClient(api_key)

    # Perform the search
    results = serp_client(search_query, location=location)

    # Check if the search was successful
    if isinstance(results, dict):
        # Format and return the top search results as JSON with updated key names
        top_results = format_top_search_results(results)
        return json.dumps({"top_results": top_results}, indent=2)
    else:
        # Handle the error response
        status_code, error_message = results
        error_json = json.dumps({"error": f"Search failed with status code {status_code}: {error_message}"})
        logger.error(error_json)
        return error_json


if __name__ == "__main__":
    search_query = "Best gyros in Barcelona, Spain"
    result_json = search(search_query, '')
    print(result_json)