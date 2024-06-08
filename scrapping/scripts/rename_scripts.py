import os 
import re
import json
import shutil
path="grey_transcripts"
destenation_path="grey_transcripts_new"
os.makedirs(destenation_path,exist_ok=True)
met_epiosdes_names={}
count={}
for file_name in os.listdir(path):
    if 'x' in file_name:
        season_number=file_name.split("x")[0].split("_")[-1]
        if season_number not in count:
            count[season_number]=0
        count[season_number]+=1
        episode_number=file_name.split("x")[1].split("_")[0]
        episode_name=file_name.split("x")[1].split("_")[-1][:-4]
        new_name=f"grey_season_{season_number}_episode_{episode_number}.txt"
        met_epiosdes_names[f"season_{season_number}_episode_{episode_number}"]=episode_name
        shutil.copyfile(f"{path}/{file_name}",f"{destenation_path}/{new_name}")

with open('grey_episodes_names.json','w') as f:
    json.dump(met_epiosdes_names,f)
    
print(count)
    
        
        
        