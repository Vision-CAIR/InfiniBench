import os 
import json 
import random 
# set the seed for reproducibility
random.seed(72) # it is my birthday 7th of February
from tqdm import tqdm

import argparse
parser = argparse.ArgumentParser(description="question-answer-generation")
parser.add_argument("--scrapped_spoiler_questions",required=True,help="path to the scrapped spoiler questions data")

args = parser.parse_args()


spoiler_questions=json.load(open(args.scrapped_spoiler_questions, 'r'))
print("number of movies in the spoiler questions data: ",len(spoiler_questions))
benchmark_data=[]
for movie in tqdm(spoiler_questions,desc="Processing MovieNet data"):
    qa_list=spoiler_questions[movie]
    video_path=f"/{movie}"
    for qa in qa_list ['questions']:
        question=qa['question']
        answer=qa['answer']
        data={}
        data['question']=question
        data['video_path_mp4']=video_path+'.mp4'
        data['video_path_frames']=video_path
        data['video_subtitles']=video_path+'.srt'   
        data['answer']=answer
        benchmark_data.append(data)
    
print(f"Total number of questions generated: {len(benchmark_data)}")
with open('../benchmark/final/mcq_open_ended/spoiler_questions.json','w') as f:
    json.dump(benchmark_data,f,indent=4)