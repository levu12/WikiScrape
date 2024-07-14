import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import argparse
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_wikipedia(keyword):
    base_url = "https://en.wikipedia.org/wiki/"
    encoded_keyword = urllib.parse.quote(keyword)
    url = base_url + encoded_keyword
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove elements with the class "navbox, sidebar, infobox"
        for element in soup.find_all(class_="navbox"):
            element.extract()

        for element in soup.find_all(class_="sidebar"):
            element.extract()

        for element in soup.find_all(class_="infobox"):
            element.extract()
        
        data = extract_data(soup)
        
        safe_filename = keyword.replace(" ", "_")
        save_as_json(data, f"{safe_filename}.json")
        convert_to_markdown(data, f"{safe_filename}.md")
        logging.info(f"Scraping completed for '{keyword}'")

    except requests.RequestException as e:
        logging.error(f"Error fetching the page: {e}")
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def extract_data(soup):
    data = {}
    data['title'] = soup.find(id="firstHeading").text if soup.find(id="firstHeading") else "Unknown Title"
    content = soup.find(id="mw-content-text")
    if content:
        data['sections'] = extract_sections(content)
        data['links'] = extract_links(content)
        data['tables'] = extract_tables(content)
    return data

def extract_sections(content):
    sections = []
    current_section = {"title": "Introduction", "content": []}
    
    for element in content.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol']):
        if element.name.startswith('h'):
            if current_section['content']:
                sections.append(current_section)
            current_section = {"title": clean_text(element.text.strip()), "content": []}
        elif element.name == 'p':
            current_section['content'].append({"type": "paragraph", "text": clean_text(element.text)})
        elif element.name in ['ul', 'ol']:
            current_section['content'].append({"type": "list", "items": [clean_text(li.text) for li in element.find_all('li')]})
    
    if current_section['content']:
        sections.append(current_section)
    
    return sections

def extract_links(content):
    links = content.find_all('a', href=True)
    external_links = []
    for link in links:
        href = link['href']
        # Check if the link is an external link (starts with 'http' or '//') and not an internal reference
        if (href.startswith('http') or href.startswith('//')) and not href.startswith('#cite_note'):
            external_links.append({
                'text': clean_text(link.text),
                'href': href
            })
    return external_links

def extract_tables(content):
    tables = content.find_all('table', class_='wikitable')
    return [table_to_dict(table) for table in tables]

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text)  # Remove citation brackets
    text = re.sub(r'\(listen\)', '', text)
    text = re.sub(r'\^', '', text)  # Remove standalone carets
    return text.strip()

def table_to_dict(table):
    rows = table.find_all('tr')
    if not rows:
        return []

    headers = [clean_text(th.text) for th in rows[0].find_all(['th', 'td'])]
    if not headers:
        max_columns = max(len(row.find_all(['th', 'td'])) for row in rows)
        headers = [f"Column {i+1}" for i in range(max_columns)]

    data = []
    for row in rows[1:]:
        cells = row.find_all(['th', 'td'])
        if cells:
            row_data = {}
            for i, cell in enumerate(cells):
                header = headers[i] if i < len(headers) else f"Column {i+1}"
                row_data[header] = clean_text(cell.text)
            data.append(row_data)

    return data

def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def convert_to_markdown(data, filename):
    md_content = f"# {data['title']}\n\n"
    
    for section in data['sections']:
        md_content += f"## {section['title']}\n\n"
        for content in section['content']:
            if content['type'] == 'paragraph':
                md_content += f"{content['text']}\n\n"
            elif content['type'] == 'list':
                for item in content['items']:
                    md_content += f"- {item}\n"
                md_content += "\n"
    
    md_content += "## External Links\n\n"
    for link in data['links']:
        md_content += f"- [{link['text']}]({link['href']})\n"
    
    md_content += "\n## Tables\n\n"
    for table in data['tables']:
        if table:
            headers = table[0].keys()
            md_content += "| " + " | ".join(headers) + " |\n"
            md_content += "| " + " | ".join(["---" for _ in headers]) + " |\n"
            for row in table:
                md_content += "| " + " | ".join(str(row.get(header, "")) for header in headers) + " |\n"
            md_content += "\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Wikipedia article")
    parser.add_argument("keyword", nargs='+', help="Keyword to search on Wikipedia (can be multiple words)")
    args = parser.parse_args()
    
    # Join multiple words into a single keyword
    keyword = ' '.join(args.keyword)
    
    scrape_wikipedia(keyword)