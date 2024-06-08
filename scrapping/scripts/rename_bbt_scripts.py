import os 
import re
import json
import shutil
path="bbt_scripts_new"
destenation_path="bbt_scripts_new_new"
os.makedirs(destenation_path,exist_ok=True)
count={}
for file_name in os.listdir(path):
    if 'x' in file_name:
        season_number=file_name.split("_")[0][1:]
        if season_number not in count:
            count[season_number]=0
        count[season_number]+=1
        episode_number=file_name.split("_")[1][1:-4]
        new_name=f"bbt_season_{season_number}_episode_{episode_number}.txt"
        shutil.copyfile(f"{path}/{file_name}",f"{destenation_path}/{new_name}")

    
print(count)
    
        
        
        