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
parser.add_argument("--gpt4_descriptions",required=True)
parser.add_argument("--existed_episodes",default="../../existed_videos_tvqa.json")

args = parser.parse_args()

pool_of_questions=[
    "what is the correct squence of changing the outfits for {} in this episode?",
    "Can you outline the order of changing the outfits for {} in this episode?",
    "What is the sequence of outfit changes for {} in this episode?",
    "How does {}'s attire evolve throughout this episode?",
    "Can you list the order of outfits worn by {} in this episode?",
    "What are the correct squence of outfits {} wears in this episode",
    "How does {}'s clothing change from the beginning to the end of this episode?",
    "In what order does {} change outfits in this episode?",
    "What are the stages of {}'s outfit changes in this episode?",
    "Can you describe the order in which {} changes clothes in this episode?",
    "How does {}'s wardrobe shift throughout this episode?",
    "Can you detail the series of outfit changes for {} in this episode?",
    "What are the chronological outfit changes for {} in this episode?",
    "What are the various outfits {} wears in this episode, listed in order?",
    "Can you track the sequence of {}'s outfit changes in this episode?",
    "What are the sequential outfits worn by {} in this episode?",
    "How do {}'s clothes change throughout this episode?",
    "Can you identify the order of costume changes for {} in this episode?",
]



 
benchmark_data=[]  
ann_path=args.gpt4_descriptions
existed_episodes=json.load(open(args.existed_episodes,'r'))

def generate_open_ended_answers(list_of_apparences):
    answer_str="First the appearance is "
    for appearance in list_of_apparences:
        answer_str+=appearance+" then "
    return answer_str[:-5]

global_apperance_data = json.load(open(ann_path, 'r'))
for season in tqdm(global_apperance_data):
    for episode in global_apperance_data[season]:
        for character in global_apperance_data[season][episode]:
            if f"/bbt/{season}/{episode}" not in existed_episodes:
                continue
            correct_answer = global_apperance_data[season][episode][character].copy()
            answer_open_ended = generate_open_ended_answers(correct_answer)
            random_q = random.choice(pool_of_questions)
            question = random_q.format(character)
            data = {}
            data['question'] = question
            data['show'] = "bbt"
            data['season'] = season
            data['episode'] = episode
            data['source'] = "tvqa"
            data['character'] = character
            data['answer'] = answer_open_ended
            data['video_path_mp4'] = f"/bbt/{season}/{episode}.mp4"
            data['video_path_frames'] = f"/bbt/{season}/{episode}"
            data['video_subtitles'] = f"/bbt/{season}/{episode}.srt"
            benchmark_data.append(data)
os.makedirs("../../benchmark", exist_ok=True)
with open('../../benchmark/global_appreance_open_ended.json', 'w') as f:
    json.dump(benchmark_data, f, indent=4)
            
        
        
        
        
        
        