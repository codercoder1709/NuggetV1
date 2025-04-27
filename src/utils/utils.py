import requests

def fetch_data(url):
    """Fetches HTML content from a given URL."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) # Add a User-Agent
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def handle_errors(error):
    """Placeholder for error handling logic."""
    # In a real application, you might log errors or implement retry logic
    print(f"An error occurred: {error}")
