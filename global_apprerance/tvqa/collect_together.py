import os
import json 
import cv2
from tqdm import tqdm
import re
import shutil
bbt_main_characters={
    "Leonard":True,
    "Sheldon":True,
    "Penny":True,
    "Howard":True,
    "Raj":True,
    "Bernadette":True,
    "Amy":True,
    "Stuart":True,
    "Emily":True,
    "Leslie":True,
    }
def make_main_characters_folders (episode_path):
    for character in bbt_main_characters:
        os.makedirs(os.path.join(episode_path,character),exist_ok=True)
def extract_season_episode(video_name):
    # Define a regex pattern to match season and episode numbers
    pattern = r's(\d+)e(\d+)'

    # Use re.search to find the pattern in the video name
    match = re.search(pattern, video_name, re.IGNORECASE)

    if match:
        # Extract season and episode numbers from the matched groups
        season_number = int(match.group(1))
        episode_number = int(match.group(2))
        return f"season_{season_number}", f"episode_{episode_number}"
    else:
        # Return None if the pattern is not found
        return None, None
  
data={}  
for clip_name in os.listdir('character_cropped_images_clips'):
    season, episode = extract_season_episode(clip_name)
    if season and episode:
        # Create a directory for the season if it does not exist
        if season not in data:
            data[season] = {}
        
        # Create a directory for the episode if it does not exist
        if episode not in data[season]:
            data[season][episode] = {}
            data[season][episode]['clips'] = []
        
        data[season][episode]['clips'].append(clip_name)
        
for season in data:
    for episode in data[season]:
        print(f"Season: {season}, Episode: {episode}")
        episode_path=f"bbt_appearance_new/{season}/{episode}"
        os.makedirs(episode_path, exist_ok=True)
        make_main_characters_folders(episode_path)
        characters_num={
            "Leonard":0,
            "Sheldon":0,
            "Penny":0,
            "Howard":0,
            "Raj":0,
            "Bernadette":0,
            "Amy":0,
            "Stuart":0,
            "Emily":0,
            "Leslie":0,
            }
        for clip in sorted(data[season][episode]['clips']):
            # print(f"Clip: {clip}")
            clip_path = os.path.join('character_cropped_images_clips', clip)
            for character in sorted(os.listdir(clip_path)):
                for frame in sorted(os.listdir(os.path.join(clip_path, character))):
                    character_path = os.path.join(episode_path, character,str(characters_num[character]).zfill(5)+".jpg")
                    frame_path = os.path.join(clip_path, character, frame)
                    # copy the frame to the character folder
                    shutil.copy(frame_path, character_path)
                    characters_num[character]+=1
            
        