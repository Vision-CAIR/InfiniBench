import os

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def scrape_imdb_summary(movie_id, season, episode):
    url = f"https://www.imdb.com/title/{movie_id}/plotsummary"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        summary_content = soup.find_all("div", {"class": "ipc-html-content-inner-div"})[-1]
        movie_summary = summary_content.get_text()
        return movie_summary
    else:
        return None


with open('movie1K.list.txt', 'r') as f:
    movie_ids = f.readlines()
movie_ids = [movie_id.strip() for movie_id in movie_ids]
results = {}
for movie_id in tqdm(movie_ids):
    summary = scrape_imdb_summary(movie_id, 1, 1)
    results[movie_id] = summary
    if not summary:
        print("Failed to retrieve the summary for movie_id: ", movie_id)
# save the results to a file
import json
with open("movienet_summaries.json", "w") as f:
    json.dump(results, f)