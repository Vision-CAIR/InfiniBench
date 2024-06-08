import os
import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

def scrape_imdb_movie_duration(movie_id):
    url = f"https://www.imdb.com/title/{movie_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        movie_duration_list = soup.find_all("li", {"class": "ipc-inline-list__item"})
        for item in movie_duration_list:
            # return the duration if it is found in the list  the duration is like 1h 39m
            # use regex to extract the duration because sometimes the duration is doesn't have minutes
            pattern = re.compile(r'\d+h\s\d+m|\d+h')
            match = pattern.search(item.text)
            if match:
                return match.group()
        # return None if the duration is not found
        return None
    else:
        return None

# 1h 46m 
def convert_time_str_to_min(duration_str):
    hours=int(duration_str.split('h')[0])
    if 'm' in duration_str:
        min=int(duration_str.split('h')[1].replace('m',''))
        total_min=hours*60+min
    else:
        total_min=hours*60
    return total_min
# duration_str = scrape_imdb_movie_duration("tt7672188")
# duration=convert_time_str_to_min(duration_str)
# print(duration)
with open('movie1K.list.txt', 'r') as f:
    movie_ids = f.readlines()
movie_ids = [movie_id.strip() for movie_id in movie_ids]
if os.path.exists("movienet_duration.json"):
    movienet_duration=json.load(open("movienet_duration.json",'r'))
else:
    movienet_duration={}
for movie_id in tqdm(movie_ids):
    try :
        movienet_duration[movie_id]=convert_time_str_to_min(movienet_duration[movie_id])
    except:
        print("failed to convert the duration for movie_id: ", movie_id)
        duration = scrape_imdb_movie_duration(movie_id)
        if not duration:
            print("Failed to retrieve the duration for movie_id: ", movie_id)
        else:
            duration_min=convert_time_str_to_min(duration)
            movienet_duration[movie_id] = duration_min
    
# save the results to a file
with open("movienet_duration.json", "w") as f:
    json.dump(movienet_duration, f)