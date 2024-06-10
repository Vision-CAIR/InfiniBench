import os 
import re
import json 
import ast 
import random
# set the seed for reproducibility 
random.seed(72) # it is my birthday 7th of February
import argparse
parser = argparse.ArgumentParser(description="question-answer-generation")
parser.add_argument("--gpt4_output",required=True)

args = parser.parse_args()

with open (args.gpt4_output,'r') as f:
    char_actions_qa_data=json.load(f)
def convert_answer_to_string(actions_list):
    answer_str="First, "
    for i,action in enumerate(actions_list):
        if i==len(actions_list)-1:
            answer_str+=action
        else:
            answer_str+=action+" then, "
    
    return answer_str
character_actions_qa=[]   
for key_name in char_actions_qa_data:
    # grey_season_03_episode_23
    name_list=key_name.split('_')
    show_name=name_list[0]
    season="season_"+name_list[2]
    episode="episode_"+name_list[4]
    for qa in char_actions_qa_data[key_name]:
        question=qa['Q']
        correct_answer=qa['A'].copy() # list of actions
        answer_str=convert_answer_to_string(correct_answer)
        data={}
        data['question']=question
        data['answer']=answer_str
        data['season']=season
        data['episode']=episode
        data['show']=show_name
        data['video_path']=f"/{show_name}/{season}/{episode}.mp4"
        data['video_path_frames']=f"/{show_name}/{season}/{episode}"
        data['video_subtitles'] = f"{show_name}/{season}/{episode}.srt"
        character_actions_qa.append(data)
        

os.makedirs("../../benchmark",exist_ok=True)
with open ('../../benchmark/tvqa_character_actions_open_ended.json','w') as f:
    json.dump(character_actions_qa,f,indent=4)
    
    
    
    
    