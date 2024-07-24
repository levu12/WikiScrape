import json

def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4) 

def convert_to_markdown(data, filename):
    md_content = f"# {data['title']}\n\n"
    
    for section in data['sections']:  # Convert each section to markdown
        md_content += f"## {section['title']}\n\n"
        for content in section['content']:
            if content['type'] == 'paragraph':
                md_content += f"{content['text']}\n\n"
            elif content['type'] == 'list':
                for item in content['items']:
                    md_content += f"- {item}\n"
                md_content += "\n"
    
    md_content += "## External Links\n\n"  # Add external links
    for link in data['links']:
        md_content += f"- [{link['text']}]({link['href']})\n"
    
    md_content += "\n## Tables\n\n"  # Add tables
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