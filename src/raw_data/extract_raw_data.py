import json
import os
import sys

# Adjust path to import from sibling directory 'scraper'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level to the project root
sys.path.insert(0, project_root)  # Add project root to sys.path

from src.scraper.restaurant_scraper import RestaurantScraper

# Corrected path construction
script_dir = os.path.dirname(__file__)
config_path = os.path.join(script_dir, '..', 'config', 'sites.json')
# Normalize the path to handle '..' correctly
config_path = os.path.normpath(config_path)

def load_config(path):
    """Loads the site configuration from the given path."""
    if not os.path.exists(path):
        print(f"Error: Configuration file not found at {path}")
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if "sites" not in config or not config["sites"]:
            print(f"Error: No sites found in {path} or the file is invalid.")
            return None
        return config
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred loading {path}: {e}")
        return None

def extract_and_save_raw_data():
    """Extract raw data from restaurant URLs and save to raw_extracted_data.json."""
    sites_config = load_config(config_path)  # Use the corrected config_path

    if not sites_config:
        print('Error: Failed to load configuration. Exiting.')
        return

    all_extracted_data = []  # List to store all extracted data

    for site in sites_config['sites']:
        url = site.get('url')
        name = site.get('name', url)  # Use name if available, otherwise URL

        if not url:
            print(f"Skipping site entry without a URL: {site}")
            continue

        try:
            print(f"\n>>> Scraping: {name} ({url})")  # Added print statement
            scraper = RestaurantScraper(url)
            restaurant_data = scraper.scrape()
            if restaurant_data:
                print(f"--- Successfully scraped data for {name} ---")
                all_extracted_data.append(restaurant_data)  # Append to the list
            else:
                print(f"--- No data returned from scraping {name} ---")  # Added else case
        except Exception as error:
            print(f"Error scraping {url}: {error}")
            import traceback
            traceback.print_exc()  # Print full traceback for scraping errors

    # Save all extracted data to raw_extracted_data.json (replacing existing data)
    # Use project_root to place the output directory correctly within src/output/
    output_dir = os.path.join(project_root, 'output')
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    output_path = os.path.join(output_dir, 'raw_extracted_data.json')
    try:  # Added try-except for file writing
        with open(output_path, 'w', encoding='utf-8') as f:  # Open in write mode to replace content
            json.dump(all_extracted_data, f, indent=4, ensure_ascii=False)
        print(f"\n>>> Saved extracted data for {len(all_extracted_data)} sites to {output_path}")
    except Exception as e:
        print(f"Error writing data to {output_path}: {e}")


if __name__ == "__main__":
    extract_and_save_raw_data()
