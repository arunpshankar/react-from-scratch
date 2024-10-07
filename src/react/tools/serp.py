from src.config.logging import logger
from src.utils.io import load_yaml
from typing import Union
from typing import Tuple
from typing import Dict
from typing import Any 
import requests
import json 

# Static paths
CREDENTIALS_PATH = './credentials/key.yml'
SEARCH_RESULTS_OUTPUT_PATH = './data/patterns/web_search/output/search/top_search_results.json'


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

    def search(self, query: str, engine: str = "google", location: str = "") -> Union[Dict[str, Any], Tuple[int, str]]:
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


def log_top_search_results(results: Dict[str, Any], top_n: int = 10) -> None:
    """
    Log the top N search results in a formatted manner.

    Parameters:
    -----------
    results : Dict[str, Any]
        The search results returned from the SERP API.
    top_n : int, optional
        The number of top search results to log (default is 10).
    """
    logger.info(f"Top {top_n} Search Results:")
    for i, result in enumerate(results.get('organic_results', [])[:top_n], start=1):
        logger.info(f"Result #{i}:")
        logger.info(f"  Position: {result.get('position')}")
        logger.info(f"  Title: {result.get('title')}")
        logger.info(f"  Link: {result.get('link')}")
        logger.info(f"  Snippet: {result.get('snippet')}")
        logger.info('-' * 100)


def save_top_search_results_to_json(results: Dict[str, Any], output_path: str, top_n: int = 10) -> None:
    """
    Save the top N search results to a JSON file in a formatted manner.

    Parameters:
    -----------
    results : Dict[str, Any]
        The search results returned from the SERP API.
    output_path : str
        The file path where the JSON file will be saved.
    top_n : int, optional
        The number of top search results to save (default is 10).
    """
    top_results = []
    for i, result in enumerate(results.get('organic_results', [])[:top_n], start=1):
        top_results.append({
            "Position": result.get('position'),
            "Title": result.get('title'),
            "Link": result.get('link'),
            "Snippet": result.get('snippet')
        })

    with open(output_path, 'w') as json_file:
        json.dump({"Top Results": top_results}, json_file, indent=4)

    logger.info(f"Top {top_n} search results saved to {output_path}")


def run(search_query: str, location: str):
    """
    Main function to execute the Google search using SERP API, log the top results,
    and save them to a JSON file.

    Parameters:
    -----------
    search_query : str
        The search query to be executed using the SERP API.
    location : str
        The location to include in the search query.
    """

    # Load the API key
    api_key = load_api_key(CREDENTIALS_PATH)

    # Initialize the SERP API client
    serp_client = SerpAPIClient(api_key)

    # Perform the search
    results = serp_client.search(search_query, location=location)

    # Check if the search was successful
    if isinstance(results, dict):
        # Log the top search results
        log_top_search_results(results)

        # Save the top search results to a JSON file
        save_top_search_results_to_json(results, SEARCH_RESULTS_OUTPUT_PATH)
    else:
        # Handle the error response
        status_code, error_message = results
        logger.error(f"Search failed with status code {status_code}: {error_message}")


if __name__ == "__main__":
    search_query = "greek restaurants"
    location = 'frisco, texas'
    run(search_query, location)
