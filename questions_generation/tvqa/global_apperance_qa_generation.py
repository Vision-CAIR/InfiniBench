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

MCQ_header="Choose the correct option for the following question: "
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

distractors = [
    ["blue jeans and white t-shirt", "black blazer and gray trousers", "navy blue gym shorts and tank top","red carpet gown with sequins"],
    ["pink pajamas", "white blouse and black pencil skirt", "red sequined party dress","red carpet gown with sequins"],
    ["khaki pants and blue polo shirt", "green soccer jersey and shorts", "black cocktail dress","black running shorts and a white tank top"],
    ["floral bathrobe", "yellow sundress", "white chef's coat and hat","black running shorts and a white tank top"],
    ["gray hoodie and ripped jeans", "silver evening gown", "purple loungewear set","floral spring dress","light blue summer dress"],
    ["red tracksuit", "blue school uniform with a plaid skirt", "gold sequin dress"],
    ["striped sleepwear set", "navy blue business suit", "light blue summer dress"],
    ["black yoga pants and a pink tank top", "red casual dress", "black tuxedo", "red casual dress", "black tuxedo"],
    ["green bikini", "denim shorts and a white blouse", "black evening gown"],
    ["white winter coat and brown boots", "floral spring dress", "red carpet gown with sequins"],
    ["black leggings and a gray sweatshirt", "blue jeans and a white sweater", "black tuxedo"],
    ["yellow raincoat", "gray business suit", "silver party dress","black running shorts and a white tank top"],
    ["blue flannel pajamas", "red weekend outfit with jeans and a t-shirt", "blue silk evening dress"],
    ["black yoga pants and purple sports bra", "white sundress", "black formal suit","black running shorts and a white tank top"],
    ["blue overalls and a white t-shirt", "red polka dot dress", "black cocktail dress"],
    ["gray sweatpants and a white hoodie", "navy blue blazer and khaki pants", "green evening gown"],
    ["black running shorts and a white tank top", "blue jeans and a red plaid shirt", "black suit and tie"],
    ["white apron and chef's hat", "denim jacket and black pants", "emerald green evening dress"],
    ["purple workout leggings and a pink top", "black business suit", "yellow summer dress","red swimsuit", "white t-shirt and khaki shorts", "blue evening gown"],
    ["red swimsuit", "purple workout leggings and a pink top","white t-shirt and khaki shorts", "blue evening gown"]
]

def generate_unique_options(correct_answer, num_options=3):
    global distractors
    # choose 4 random distractors without replacement
    distractor_1, distractor_2, distractor_3, distractor_4 = random.sample(distractors, 4)
    options = [distractor_1]
    all_events = correct_answer.copy()
    if len(all_events)==2:
        num_options=2
        options = [distractor_1, distractor_2, distractor_3]
        print("events are only 2", all_events)
    if len(all_events)==1:
        num_options=1
        options = [distractor_1, distractor_2, distractor_3,distractor_4]
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
ann_path=args.gpt4_descriptions
existed_episodes=json.load(open(args.existed_episodes,'r'))

global_apperance_data = json.load(open(ann_path, 'r'))
for season in tqdm(global_apperance_data):
    for episode in global_apperance_data[season]:
        for character in global_apperance_data[season][episode]:
            if f"/bbt/{season}/{episode}" not in existed_episodes:
                continue
            correct_answer = global_apperance_data[season][episode][character].copy()
            options = generate_unique_options(correct_answer)
            options.append(correct_answer)
            # add I don't know option
            options.append("I don't know")
            random_q = random.choice(pool_of_questions)
            question = f"{MCQ_header} {random_q.format(character)}"
            # shuffle the options
            random.shuffle(options)
            if len(options) != 6:
                print("number of options: ", len(options))
            
            answer_key = options.index(correct_answer)
            data = {}
            data['answer_idx'] = answer_key
            data['options'] = options
            data['question'] = question
            data['show'] = "bbt"
            data['season'] = season
            data['episode'] = episode
            data['source'] = "tvqa"
            data['character'] = character
            data['video_path_mp4'] = f"/bbt/{season}/{episode}.mp4"
            data['video_path_frames'] = f"/bbt/{season}/{episode}"
            data['video_subtitles'] = f"/bbt/{season}/{episode}.srt"
            benchmark_data.append(data)
os.makedirs("../../benchmark", exist_ok=True)
with open('../../benchmark/global_appreance.json', 'w') as f:
    json.dump(benchmark_data, f, indent=4)
            
        
        
        
        
        
        