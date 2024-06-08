import os
import json
import requests
from bs4 import BeautifulSoup
import re 

def clean_script(script):
    script=script.replace("<div class='full-script'>",'')
    script=script.replace('<br>','\n')
    script=script.replace('</br>','')
    return script
def remove_html_tags(text):
    text=text.replace('<br/>', '\n').replace('<br>', '\n')
    clean_text = re.sub(r'<[^>]*>', '', text)
    # remove empty lines and lines with only spaces 
    clean_text = os.linesep.join([s for s in clean_text.splitlines() if s.strip()])
    # remove this character like @#*&!= 
    clean_text=clean_text.replace('@','')
    clean_text=clean_text.replace('#','')
    clean_text=clean_text.replace('*','')
    clean_text=clean_text.replace('&','')
    clean_text=clean_text.replace('!','')
    clean_text=clean_text.replace('=','')
    return clean_text
    
def scrape_script(show_name='/series/Castle-1219024'):
    base_url = f"https://subslikescript.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    show_url=base_url+show_name
    response = requests.get(show_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        seasons = []
        for seasons_html in soup.find_all("div", {"class": "season"}):
            season_soup = BeautifulSoup(str(seasons_html), 'html.parser')
            urls = [link['href'] for link in season_soup.find_all('a')]
            seasons.append(urls)
        results={}
        for i,season in enumerate(seasons): 
            os.makedirs(show_name.split('/')[-1], exist_ok=True)
            for j,episodes_url in enumerate(season) :
                full_url=base_url+episodes_url
                print(full_url)
                episode_soup=BeautifulSoup(requests.get(full_url, headers=headers).text, 'html.parser')
                script=str(episode_soup.find_all("div", {"class": "full-script"})[0])
                
                script=remove_html_tags(script)
                with open (f"{show_name.split('/')[-1]}/s{str(i).zfill(2)}_e{str(j).zfill(2)}.txt", "w") as f:
                    f.write(script)
                if f"season_{i}" not in results:
                    results[f"season_{i}"]={}
                if f"episode_{j}" not in results[f"season_{i}"]:
                    results[f"season_{i}"][f"episode_{j}"]={}
                results[f"season_{i}"][f"episode_{j}"]=script
                break
        
        with open(f"{show_name.split('/')[-1]}/scripts.json", "w") as f:
            json.dump(results, f)
    #         if 'title' in episode_url['href']:
    #             episodes_urls.append(episode_url['href'])
    #     episode_url = episodes_urls[episode]
    #     episode_url = f"https://www.imdb.com{episode_url}"
    #     # print(episode_url)
    #     episode_id = episode_url.split('/')[-2]
    #     summary_url = f"https://www.imdb.com/title/{episode_id}/plotsummary"
    #     # print(summary_url)
    #     summary_response = requests.get(summary_url, headers=headers)
    #     summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
    #     summary_content = summary_soup.find_all("div", {"class": "ipc-html-content-inner-div"})[-1]
    #     episode_summary = summary_content.get_text()
    #     return episode_summary
    # else:
    #     return None

# tvqa_ids={"friends":"tt0108778",
#          "house":"tt0412142",
#          "bbt":"tt0898266",
#          "grey":"tt0413573",
#          "met":"tt0460649",
#          "castle":"tt1219024",
#          }
# tvqa_dir="/ibex/project/c2106/kirolos/Long_TVQA/videos/"
# results={}
# count=0
# for series in tvqa_ids:
#     series_id=tvqa_ids[series]
#     series_dir=tvqa_dir+series+"_frames"
#     for season in os.listdir(series_dir):
#         season_number=int(season.split("_")[-1])
#         for episode in os.listdir(series_dir+"/"+season):
#             episode_number=int(episode.split("_")[-1])
#             count+=1
#             # summary = scrape_imdb_summary(series_id, season_number, episode_number)
#             # if series not in results:
#             #     results[series]={}
#             # if season not in results[series]:
#             #     results[series][season]={}
#             # results[series][season][episode]=summary
#             # if summary:
#             #     print(f"Successfuly got the summary for Season {season_number}, Episode {episode_number} of {series}:")
#             # else:
#             #     print("Failed to retrieve the summary.")
#             # print("--------------------------------------------------------")
# print(count)

# # # save the results to a file
# # import json
# # with open("imdb_summaries_222.json", "w") as f:
# #     json.dump(results, f)

scrape_script()
"https://subslikescript.com/series/Castle-1219024/series/Castle-1219024/season-1/episode-1-Flowers_for_Your_Grave"
"https://subslikescript.com/series/Castle-1219024/season-1/episode-1-Flowers_for_Your_Grave"
