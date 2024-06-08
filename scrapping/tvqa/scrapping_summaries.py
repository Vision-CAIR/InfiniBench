import os

import requests
from bs4 import BeautifulSoup


def scrape_imdb_summary(series_id, season, episode):
    url = f"https://www.imdb.com/title/{series_id}/episodes?season={season}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        episodes_urls = []
        for episode_url in soup.find_all("a", {"class": "ipc-lockup-overlay ipc-focusable"}):
            if 'title' in episode_url['href']:
                episodes_urls.append(episode_url['href'])
        episode_url = episodes_urls[episode]
        episode_url = f"https://www.imdb.com{episode_url}"
        # print(episode_url)
        episode_id = episode_url.split('/')[-2]
        summary_url = f"https://www.imdb.com/title/{episode_id}/plotsummary"
        # print(summary_url)
        summary_response = requests.get(summary_url, headers=headers)
        summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
        summary_content = summary_soup.find_all("div", {"class": "ipc-html-content-inner-div"})[-1]
        episode_summary = summary_content.get_text()
        return episode_summary
    else:
        return None

tvqa_ids={"friends":"tt0108778",
         "house":"tt0412142",
         "bbt":"tt0898266",
         "grey":"tt0413573",
         "met":"tt0460649",
         "castle":"tt1219024",
         }
tvqa_dir="/ibex/project/c2106/kirolos/Long_TVQA/videos/"
results={}
count=0
for series in tvqa_ids:
    series_id=tvqa_ids[series]
    series_dir=tvqa_dir+series+"_frames"
    for season in os.listdir(series_dir):
        season_number=int(season.split("_")[-1])
        for episode in os.listdir(series_dir+"/"+season):
            episode_number=int(episode.split("_")[-1])
            count+=1
            # summary = scrape_imdb_summary(series_id, season_number, episode_number)
            # if series not in results:
            #     results[series]={}
            # if season not in results[series]:
            #     results[series][season]={}
            # results[series][season][episode]=summary
            # if summary:
            #     print(f"Successfuly got the summary for Season {season_number}, Episode {episode_number} of {series}:")
            # else:
            #     print("Failed to retrieve the summary.")
            # print("--------------------------------------------------------")
print(count)

# # save the results to a file
# import json
# with open("imdb_summaries_222.json", "w") as f:
#     json.dump(results, f)