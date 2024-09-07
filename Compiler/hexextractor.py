# This file while extract all the patterns from a wiki page and store them in "output.txt" as Macros ready for use with our compiler

import requests
import re
from bs4 import BeautifulSoup

# Define the URL of your local server
url = "https://talia-12.github.io/Hexal/"

# Fetch the HTML content from the local server
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Find all elements with the class "pattern-title"
    pattern_titles = soup.find_all(class_="pattern-title")

    # Open a file to write the data
    with open('output.txt', 'w') as file:
        # Iterate over each pattern-title element
        for pattern in pattern_titles:
            # Extract the raw text inside the pattern-title element
            raw_title_text = pattern.get_text(strip=True)

            # Remove everything after the character '(' (including the character itself)
            if '(' in raw_title_text:
                parenthesis_index = raw_title_text.index('(')
                clean_title_text = raw_title_text[:parenthesis_index].strip()
            else:
                clean_title_text = raw_title_text

            # Replace spaces with underscores and remove non-alphanumeric characters
            clean_title_text = re.sub(r'[^a-zA-Z0-9 ]', '', clean_title_text)  # Remove non-alphanumeric except space
            clean_title_text = clean_title_text.replace(' ', '_')  # Replace spaces with underscores

            # Find the next sibling element (the container of spell-viz)
            sibling_container = pattern.find_next_sibling()

            # Check if the sibling container exists and contains the spell-viz element
            if sibling_container is not None:
                # Now, search for the spell-viz element inside the sibling container
                spell_viz = sibling_container.find(class_="spell-viz")

                # Check if the spell-viz element exists
                if spell_viz is not None:
                    # Extract the values of the "data-string" and "data-start" attributes
                    data_string = spell_viz.get('data-string')
                    data_start = spell_viz.get('data-start').upper()  # Convert to uppercase

                    # Format the line with clean_title_text enclosed in double quotes
                    line = f'#define {clean_title_text} <{data_start} {data_string}>\n'
                    
                    # Write the formatted line to the file
                    file.write(line)
                else:
                    file.write(f'#define "{clean_title_text}" <N/A N/A>\n')
            else:
                file.write(f'#define "{clean_title_text}" <N/A N/A>\n')
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")