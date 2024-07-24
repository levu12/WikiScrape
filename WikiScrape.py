import requests
from bs4 import BeautifulSoup
import extract
import save
import urllib.parse
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  

def scrape_wikipedia(keyword):
    base_url = "https://en.wikipedia.org/wiki/"
    encoded_keyword = urllib.parse.quote(keyword)
    url = base_url + encoded_keyword
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove elements with the class "navbox, sidebar, infobox"
        for element in soup.find_all(class_="navbox"):
            element.extract()

        for element in soup.find_all(class_="sidebar"):
            element.extract()

        for element in soup.find_all(class_="infobox"):
            element.extract()
        
        data = extract.extract_data(soup)
        
        # Make filename safe by replacing spaces with underscores
        safe_filename = keyword.replace(" ", "_")
        save.save_as_json(data, f"{safe_filename}.json")
        save.convert_to_markdown(data, f"{safe_filename}.md")
        logging.info(f"Scraping completed for '{keyword}'")

    except requests.RequestException as e:
        logging.error(f"Error fetching the page: {e}")
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="Scrape Wikipedia article")  
    parser.add_argument("keyword", nargs='+', help="Keyword to search on Wikipedia (can be multiple words)")
    args = parser.parse_args()
    
    # Join multiple words into a single keyword
    keyword = ' '.join(args.keyword)
    
    scrape_wikipedia(keyword)