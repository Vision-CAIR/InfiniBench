import os
import json
import requests
from bs4 import BeautifulSoup
import re 
from tqdm import tqdm

def get_urls():
    base_url = f"https://bigbangtrans.wordpress.com/series-1-episode-1-pilot-episode/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    show_url=base_url
    response = requests.get(show_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        pages=soup.find_all("div", {"class": "widget widget_pages"})
        for page in pages:
            page_soup=BeautifulSoup(str(page), 'html.parser')
            urls = [link['href'] for link in page_soup.find_all('a')]
            filtered_urls=[]
            for url in urls:
                if 'episode' in url:
                    filtered_urls.append(url)
            return filtered_urls
        
    else:
        print("Error", response.status_code)
        return None
    
def scrap_script(episode_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(episode_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_entry_text=soup.find_all("div", {"class": "entrytext"})[0]
        entry_text_soup=BeautifulSoup(str(soup_entry_text), 'html.parser')
        script_texts=entry_text_soup.find_all("p")
        text=""
        for i,script_text in enumerate(script_texts):
            script=script_text.get_text()
            text+=script+'\n'
        return text
    else:
        print("Error", response.status_code)
        return None
        
        
        
        
        
        
urls=get_urls()
os.makedirs('bbt_scripts_new', exist_ok=True)
print(f"Scraping scripts: {len(urls)}")
for url in tqdm(urls):
    print(url)
    script=scrap_script(url)
    season=int(url.split('-')[1])
    episode=int(url.split('-')[3])
    with open (f"bbt_scripts_new/s{str(season).zfill(2)}_e{str(episode).zfill(2)}.txt", "w") as f:
        f.write(script)
    
