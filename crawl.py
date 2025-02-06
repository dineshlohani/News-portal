import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import re

def extract_data_from_div(url):
    data = {}
    response = requests.get(url)    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        detail_div = soup.find('div', class_='detail b-shadow margin-bottom-20')
        if detail_div:
            for tag in detail_div.find_all(True):
                del tag['class']
                del tag['style']
                del tag['id']
            for ul_tag in detail_div.find_all('ul'):
                ul_tag.extract()
            for li_tag in detail_div.find_all('li'):
                li_tag.extract()
            for a_tag in detail_div.find_all('a'):
                a_tag.extract()
            div_content = str(detail_div)

            div_content_without_newlines = div_content.replace('\n', '')

            h5_tags = detail_div.find_all('h5')
            time_text = ""
            for h5_tag in h5_tags:
                time_text += ''.join(h5_tag.find_all(text=True, recursive=False))

            try:
                parsed_time = date_parser.parse(time_text.strip())

                formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
                data["div_content_without_newlines"] = div_content_without_newlines
                data["time"] = formatted_time
            except Exception as e:
                data["error"] = f"Error occurred while parsing time: {e}"
        else:
            data["error"] = "No data found in the specified <div> element."
    else:
        data["error"] = f"Failed to retrieve data from the URL: {response.status_code}"

    return data
