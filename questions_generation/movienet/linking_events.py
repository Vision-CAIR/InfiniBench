import os 
import json 
import random 
# set the seed for reproducibility
random.seed(72) # it is my birthday 7th of February
from tqdm import tqdm

import argparse
parser = argparse.ArgumentParser(description="question-answer-generation")
parser.add_argument("--gpt4_output",required=True)

args = parser.parse_args()

linking_events_data=json.load(open(args.gpt4_output, 'r'))
benchmark_data=[]
for movie in tqdm(linking_events_data,desc="Processing MovieNet data"):
    qa_list=linking_events_data[movie]
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
os.makedirs("../../benchmark",exist_ok=True)
with open('../../benchmark/movienet_linking_events.json','w') as f:
    json.dump(benchmark_data,f,indent=4)