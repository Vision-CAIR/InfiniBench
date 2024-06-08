import os 
import json 
import random 
# set the seed for reproducibility
random.seed(72) # it is my birthday 7th of February
from tqdm import tqdm

tricky_qa=json.load(open('../skills_output_full/tricky_questions_qa_new.json', 'r'))
for question in tricky_qa:
    episode_name=question['episode_neme']
    show=episode_name.split('_')[0]
    season_number=episode_name.split('_')[2]
    episode_number=episode_name.split('_')[4]
    video_path=f"/{show}/season_{season_number}/episode_{episode_number}"
    question['show']=show
    question['season']="season_"+season_number
    question['episode']="episode_"+episode_number
    question['video_path_mp4']=video_path+'.mp4'
    question['video_path_frames']=video_path
    question['video_subtitles']=video_path+'.srt'   
    
print(f"Total number of questions generated: {len(tricky_qa)}")
with open('../benchmark/CU_tricky_questions_qa.json','w') as f:
    json.dump(tricky_qa,f,indent=4)