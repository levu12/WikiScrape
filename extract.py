import clean

def extract_data(soup):
    data = {}
    # Set the title of the article to the title of the page
    data['title'] = soup.find(id="firstHeading").text if soup.find(id="firstHeading") else "Unknown Title"
    content = soup.find(id="mw-content-text")
    if content: # Check if the content is found, and if so, extract it
        data['sections'] = extract_sections(content)
        data['links'] = extract_links(content)
        data['tables'] = extract_tables(content)
    return data

def extract_sections(content):
    sections = []
    current_section = {"title": "Introduction", "content": []}
    
    # FInd all paragraphs, links, and headings, and label and return each
    for element in content.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol']): 
        if element.name.startswith('h'):
            if current_section['content']:
                sections.append(current_section)
            current_section = {"title": clean.clean_text(element.text.strip()), "content": []}
        elif element.name == 'p':
            current_section['content'].append({"type": "paragraph", "text": clean.clean_text(element.text)})
        elif element.name in ['ul', 'ol']:
            current_section['content'].append({"type": "list", "items": [clean.clean_text(li.text) for li in element.find_all('li')]})
    
    if current_section['content']:
        sections.append(current_section)
    
    return sections

def extract_links(content):
    # Find all links in the content and extract and return the text and href attributes
    links = content.find_all('a', href=True)
    external_links = []
    for link in links:
        href = link['href']
        # Check if the link is an external link (starts with 'http' or '//') and not an internal reference
        if (href.startswith('http') or href.startswith('//')) and not href.startswith('#cite_note'):
            external_links.append({
                'text': clean.clean_text(link.text),
                'href': href
            })
    return external_links

def extract_tables(content):
    # Find all tables in the content and convert them to a list of dictionaries
    tables = content.find_all('table', class_='wikitable')
    return [clean.table_to_dict(table) for table in tables]