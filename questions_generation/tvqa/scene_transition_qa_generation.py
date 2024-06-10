import os 
import re
import json 
import ast 
import random
# set the seed for reproducibility 
random.seed(72) # it is my birthday 7th of February
from tqdm import tqdm
import argparse
parser = argparse.ArgumentParser(description="question-answer-generation")
parser.add_argument("--gpt4_output",required=True)
parser.add_argument("--existed_episodes",default="existed_videos_tvqa.json")

args = parser.parse_args()


MCQ_header="Choose the correct option for the following question: "
pool_of_questions=[
    "what is the correct squence of scene transition in this episode?",
    "Can you outline the order of scene changes in this episode?",
    "What is the correct sequence of scene transitions in this episode?",
    "Could you detail the progression of scenes in this episode?",
    "How do the scenes transition in this episode?",
    "What is the chronological order of scenes in this episode?",
    "Can you describe the sequence of events in the episode?",
    "What order do the scenes appear in this episode?",
    "How are the scenes organized in this episode?",
    "Could you list the scenes in the order they occur in this episode?",
    "What is the sequence of scene shifts in this episode?",
]

def generate_unique_options(correct_answer, num_options=4):
    options = []
    all_events = correct_answer.copy()
    if len(all_events)==2:
        num_options=2
        print("events are only 2", all_events)
    if len(all_events)==1:
        num_options=1
        print("events are only 1", all_events)
    timer=0
    for _ in range(num_options):
        while True:
            timer+=1
            random.shuffle(all_events)
            option = all_events.copy()
            if option != correct_answer and option not in options:
                options.append(option)
                break
            if timer>100:
                break

    return options

benchmark_data=[]  

existed_episodes=json.load(open(args.existed_episodes,'r'))
print("Number of existed episodes: ", len(existed_episodes))

gpt4_output=args.gpt4_output

with open (gpt4_output,'r') as f:
    scene_transitions=json.load(f)

for episode in scene_transitions:
    transitions_list=scene_transitions[episode]
    show_name=episode.split('_')[0]
    season="season_"+str(int(episode.split('_')[2]))
    episode="episode_"+str(int(episode.split('_')[4]))
    if f"/{show_name}/{season}/{episode}" not in existed_episodes:
        continue
    correct_answer=transitions_list.copy()
    options=generate_unique_options(transitions_list)
    options.append(correct_answer)
    # add I don't know option 
    options.append("I don't know")
    
    random_q=random.choice(pool_of_questions)
    question=f"{MCQ_header} {random_q}"
    # shuffle the options 
    random.shuffle(options)
    answer_key=options.index(correct_answer)
    data={}
    data['answer_idx']=answer_key
    data['options']=options
    data['question']=question
    data['show']=show_name
    data['season']=season
    data['episode']=episode
    data['source']="tvqa"
    data['video_path_mp4']=f"/{show_name}/{season}/{episode}.mp4"
    data['video_path_frames']=f"/{show_name}/{season}/{episode}"
    data['video_subtitles']=f"/{show_name}/{season}/{episode}.srt"  
    benchmark_data.append(data)
os.makedirs("../../benchmark",exist_ok=True)
with open('../../benchmark/scene_transitions.json','w') as f:
    json.dump(benchmark_data,f)
        
        
        
        
        
        
        