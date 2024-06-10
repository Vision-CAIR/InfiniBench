import os 
import json 
import random 
# set the seed for reproducibility
random.seed(72) # it is my birthday 7th of February
from tqdm import tqdm

import argparse
parser = argparse.ArgumentParser(description="question-answer-generation")
parser.add_argument("--summarization_tvqa_json",required=True,help="Path to the json file containing the summarization data for TVQA")
parser.add_argument("--summarization_movienet_json",required=True,help="Path to the json file containing the summarization data for MovieNet")
args = parser.parse_args()


summarization_questions_pool = [
    "Please provide a very detailed summary of the video.",
    "Can you give an in-depth summary of this video?",
    "Provide a comprehensive summary of the video content.",
    "Please summarize the video with as much detail as possible.",
    "Can you give a thorough overview of everything covered in the video?",
    "Describe the video content in a detailed manner.",
    "Can you provide an exhaustive summary of the video?",
    "Please break down the video content in great detail.",
    "Give a full and detailed summary of this video.",
    "Can you summarize each section of the video in detail?",
    "Provide a detailed breakdown of the video content.",
    "Please summarize the video in a comprehensive manner.",
    "Can you give a detailed summary of the video content?",
    "Provide a detailed summary of the video.",
]


tvqa_data=json.load(open(args.summarization_tvqa_json, 'r'))
benchmark_data=[]
for show in tqdm (tvqa_data,desc="Processing TVQA data"):
    for season in tvqa_data[show]:
        for episode in tvqa_data[show][season]:
            summary=tvqa_data[show][season][episode]
            video_path=f"/{show}/{season}/{episode}"
            question=random.choice(summarization_questions_pool)
            data={}
            data['question']=question
            data['video_path_mp4']=video_path+'.mp4'
            data['video_path_frames']=video_path
            data['video_subtitles']=video_path+'.srt'   
            data['answer']=summary
            data['show']=show
            data['season']=season
            data['episode']=episode
            benchmark_data.append(data)

movies_data=json.load(open(args.summarization_movienet_json,'r'))
for movie in tqdm(movies_data,desc="Processing MovieNet data"):
    summary=movies_data[movie]
    video_path=f"/{movie}"
    question=random.choice(summarization_questions_pool)
    data={}
    data['question']=question
    data['video_path_mp4']=video_path+'.mp4'
    data['video_path_frames']=video_path
    data['video_subtitles']=video_path+'.srt'   
    data['answer']=summary
    benchmark_data.append(data)
    
print(f"Total number of questions generated: {len(benchmark_data)}")
os.makedirs('../../benchmark/final',exist_ok=True)
with open('../../benchmark/final/summarization.json','w') as f:
    json.dump(benchmark_data,f,indent=4)