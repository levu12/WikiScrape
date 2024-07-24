import re

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text)  # Remove citation brackets
    text = re.sub(r'\(listen\)', '', text)
    text = re.sub(r'\^', '', text)  # Remove standalone carets
    return text.strip()

def table_to_dict(table):
    rows = table.find_all('tr')  # Find all rows in the table
    if not rows:
        return []

    headers = [clean_text(th.text) for th in rows[0].find_all(['th', 'td'])]  # Extract headers from the first row
    if not headers:
        max_columns = max(len(row.find_all(['th', 'td'])) for row in rows)  # Find the maximum number of columns in the table
        headers = [f"Column {i+1}" for i in range(max_columns)]

    data = []
    for row in rows[1:]:
        cells = row.find_all(['th', 'td'])  # Find all cells in the row
        if cells:
            row_data = {}
            for i, cell in enumerate(cells):  # Extract cell data and assign it to the corresponding header
                header = headers[i] if i < len(headers) else f"Column {i+1}"
                row_data[header] = clean_text(cell.text)
            data.append(row_data)

    return data