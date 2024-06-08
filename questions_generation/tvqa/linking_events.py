import os 
import re
import json 
import ast 
import random
# set the seed for reproducibility 
random.seed(72) # it is my birthday 7th of February


with open ('../benchmark/linking_events_final.json','r') as f:
    linking_events_data=json.load(f)
linking_events_qa=[]   
for key_name in linking_events_data:
    # grey_season_03_episode_23
    name_list=key_name.split('_')
    show_name=name_list[0]
    season="season_"+name_list[2]
    episode="episode_"+name_list[4]
    for qa in linking_events_data[key_name]:
        question=qa['Q']
        answer=qa['A']
        data={}
        data['question']=question
        data['answer']=answer
        data['season']=season
        data['episode']=episode
        data['show']=show_name
        data['video_path']=f"/{show_name}/{season}/{episode}.mp4"
        data['video_path_frames']=f"/{show_name}/{season}/{episode}"
        data['video_subtitles'] = f"{show_name}/{season}/{episode}.srt"
        linking_events_qa.append(data)
        
    
with open ('../benchmark/linking_events_tvqa.json','w') as f:
    json.dump(linking_events_qa,f,indent=4)
    
    
    
    
    