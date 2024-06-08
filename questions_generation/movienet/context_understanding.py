import os 
import json 
import random 
# set the seed for reproducibility
random.seed(72) # it is my birthday 7th of February
from tqdm import tqdm


context_understanding_data=json.load(open('../../skills_output/movienet/context_understanding_movienet_new.json', 'r'))
benchmark_data=[]
for movie in tqdm(context_understanding_data,desc="Processing MovieNet data"):
    qa_list=context_understanding_data[movie]
    video_path=f"/{movie}"
    for qa in qa_list :
        question=qa['Q']
        answer=qa['A']
        data={}
        data['question']=question
        data['video_path_mp4']=video_path+'.mp4'
        data['video_path_frames']=video_path
        data['video_subtitles']=video_path+'.srt'   
        data['answer']=answer
        benchmark_data.append(data)
    
print(f"Total number of questions generated: {len(benchmark_data)}")
with open('../../benchmark/context_understanding_movienet.json','w') as f:
    json.dump(benchmark_data,f,indent=4)