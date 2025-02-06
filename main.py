import threading
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import time
import requests
from getlink import scrape_website
from crawl import extract_data_from_div

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

first_request_made = False  # Define the flag to track the first request

lock = threading.Lock()

class NewsModel:
    @staticmethod
    def find():
        return mongo.db.news.find()

    @staticmethod
    def insert_many(news_list):
        try:
            with lock:
                mongo.db.news.insert_many(news_list)
        except Exception as e:
            print(f"Error inserting data into the database: {e}")

def scrape_single_url(url):
    try:
        data = scrape_website(url)
        existing_urls = set(mongo.db.news.distinct("link"))
        new_data = []

        for link in data.get('links', []):
            href = link.get('href')
            if href in existing_urls:
                continue

            data_from_div = extract_data_from_div(href)
            if data_from_div.get('error'):
                print(f"Error extracting data from {href}: {data_from_div['error']}")
                continue
            
            news_model = {
                "link": href,
                "news": data_from_div.get('div_content_without_newlines', ''),
                "time": data_from_div.get('time')
            }
            new_data.append(news_model)
            existing_urls.add(href)

        return new_data
    except Exception as e:
        print(f"Error scraping URL {url}: {e}")
        return []

def scrape_and_store():
    url = 'https://www.sharesansar.com/category/latest'
    data = scrape_single_url(url)
    if data:
        NewsModel.insert_many(data)
        print(f"Response time: {time.time()} seconds") 
        print(f"Thread data: {data}") 
    else:
        print("No data scraped.")

def auto_scrape_and_update():
    while True:
        scrape_and_store()
        time.sleep(900)  # Scrape every 15 minutes

@app.route('/')
def get_data():
    global first_request_made
    if not first_request_made:
        first_request_made = True
        auto_scrape_thread = threading.Thread(target=auto_scrape_and_update)
        auto_scrape_thread.start()

    existing_data = list(NewsModel.find())
    
    all_data = existing_data
    
    # Sort the combined list based on time (assuming 'time' field exists)
    all_data.sort(key=lambda x: x.get('time', float('-inf')), reverse=True)
    return render_template('index.html', data_list=all_data)

if __name__ == "__main__":
    app.run(debug=True)
