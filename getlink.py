from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_website(url, total_count_limit=40):
    firefox_options = webdriver.FirefoxOptions()
    # Remove headless mode for debugging
    # firefox_options.headless = True

    href_text_lengths = {}
    links_list = []
    next_url = url  

    while next_url:
        print(f'Total Count: {len(links_list)}')

        with webdriver.Firefox(options=firefox_options) as driver:
            driver.get(next_url)

            # Wait for the news list to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "newslist"))
            )

            page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        div_tags = soup.find_all('div', class_='newslist')

        for div_tag in div_tags:
            a_tags = div_tag.find_all('a')

            for a_tag in a_tags:
                href = a_tag.get('href')
                text = a_tag.text.strip()
                text_length = len(text.split())

                if href in href_text_lengths and text != "Next »" and text != "« Previous":
                    if text_length > href_text_lengths[href]:
                        href_text_lengths[href] = text_length
                        links_list = [link for link in links_list if link['href'] != href]
                        links_list.append({'href': href, 'text': text})
                elif text != "Next »" and text != "« Previous":
                    href_text_lengths[href] = text_length
                    links_list.append({'href': href, 'text': text})

        if len(links_list) >= total_count_limit:
            break

        next_link = soup.find('a', string='Next »')
        if next_link:
            next_href = next_link.get('href')
            next_url = urljoin(url, next_href)  # Ensure absolute URL
        else:
            next_url = None

    response = {
        'total_count': len(links_list),
        'links': links_list
    }

    return response
