import json
import os
import requests
from xml.etree import ElementTree
from collections import defaultdict
from .utils.constants import MAX_RESTAURANTS_TO_FETCH

def parse_sitemap(sitemap_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers)
    response.raise_for_status()

    root = ElementTree.fromstring(response.content)
    urls = [url.find('{*}loc').text.strip() for url in root.findall('{*}url')]
    print(f"Found {len(urls)} URLs in sitemap")
    return urls

def extract_data_from_url(url):
    """Extract restaurant details from the URL."""
    parts = url.split('/')
    if len(parts) < 5:
        return None
    return {
        "name": parts[3].replace('-', ' ').title(),
        "url": url,
        "location": parts[4].replace('-', ' ').title(),
        "Time": "10:00 AM - 11:00 PM",  # Default time for eatsure restaurants
        "contact": "+91 9523029342"     # Default contact changes when scraping
    }

def group_restaurants_by_name(urls):
    """Group restaurant data by name and include up to 2 locations."""
    grouped_data = defaultdict(list)
    for url in urls:
        data = extract_data_from_url(url)
        if data:
            grouped_data[data["name"]].append(data)
    
    # Limit each restaurant to 2 locations
    for name in grouped_data:
        grouped_data[name] = grouped_data[name][:2]
    
    return grouped_data

def update_sites_json(data, json_path):
    """Replace the sites.json file with new data."""
    new_data = {"sites": data}

    # Ensure all entries have "Time" and "contact" fields
    for entry in new_data["sites"]:
        entry.setdefault("Time", "10:00 AM - 11:00 PM")
        entry.setdefault("contact", "+91 9523029342")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4)

def main():
    sitemap_url = "https://www.eatsure.com/sitemaps/brands.xml"
    json_path = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')
    
    urls = parse_sitemap(sitemap_url)
    
    grouped_restaurants = group_restaurants_by_name(urls)

    # Select unique restaurants with all their locations up to the limit
    selected_restaurants = []
    for i, (name, locations) in enumerate(grouped_restaurants.items()):
        # Use the imported constant here
        if i >= MAX_RESTAURANTS_TO_FETCH:
            break
        selected_restaurants.extend(locations)

    update_sites_json(selected_restaurants, json_path)
    print(f"Updated {json_path} with {len(selected_restaurants)} new entries.")

if __name__ == "__main__":
    main()
