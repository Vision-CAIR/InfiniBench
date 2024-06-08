import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# URLs
main_url = "http://transcripts.foreverdreaming.org"
all_pages = [f"http://transcripts.foreverdreaming.org/viewforum.php?f=890&start={i}" for i in range(0, 500, 25)]


# Function to get episode links
def episode_getter(link):
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Failed to get episodes from {link}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    title_reference = soup.select(".topictitle")
    
    episode_links = []
    episode_names = []
    
    for title in title_reference:
        href = title['href']
        full_link = main_url + href.lstrip('.')
        episode_name = title.get_text()
        episode_links.append(full_link)
        episode_names.append(episode_name)
        
    return pd.DataFrame({
        'episode_name': episode_names,
        'link': episode_links
    })

# Get all episodes
all_episodes_list =[]
for page in all_pages:
    out=episode_getter(page) 
    if out is not None:
        all_episodes_list.append(out)
all_episodes = pd.concat(all_episodes_list, ignore_index=True)
all_episodes['id'] = range(1, len(all_episodes) + 1)

# Function to save transcripts
def save_transcript(episode_name, link, episode_id):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example selector, update according to actual structure
    transcript_text = soup.select_one('.postbody').get_text(separator="\n")
    
    # Clean up the episode name for a valid filename
    episode_name_clean = "".join([c if c.isalnum() or c.isspace() else "_" for c in episode_name])
    filename = f"house_transcripts/episode_{episode_id}_{episode_name_clean}.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(transcript_text)

# Create directory for transcripts
os.makedirs('house_transcripts', exist_ok=True)

# Save all transcripts
for _, row in all_episodes.iterrows():
    save_transcript(row['episode_name'], row['link'], row['id'])

print("All transcripts have been saved.")
