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


MCQ_header="Choose the correct option for the following question: "
distractors=[
    ["eating a Margherita pizza with extra cheese at a cozy Italian restaurant",
"sipping on a freshly brewed artisanal coffee at a quaint café",
"having an in-depth conversation with a close friend about future travel plans"],
    ["reading a mystery novel by the fireplace on a rainy day",
"jogging through a scenic trail in the early morning",
"attending a pottery class to make handmade bowls",
"visiting a local farmers' market to buy fresh produce"],
    ["enjoying a cappuccino with a dash of cinnamon at a trendy coffee shop",
"discussing the latest book club read with a friend over lunch",
"savoring a slice of gourmet pizza with sun-dried tomatoes and arugula at a pizzeria",
"exploring an art museum's new exhibit on modern sculpture"],
    ["attending a yoga class focusing on relaxation techniques",
"learning to play a new song on the piano",
"volunteering at an animal shelter to walk dogs",
"going on a guided historical tour of the city",
"planting herbs and flowers in a community garden"],
    ["playing a competitive game of football at the local park with friends",
"binge-watching the latest season of a popular TV series while lounging on the couch",
"devouring a homemade pepperoni pizza with a crispy crust while watching a movie",
"taking a scenic drive through the countryside to enjoy the views",
"visiting a planetarium to learn about constellations and planets"],
    ["hiking up a mountain trail to catch the sunrise",
"attending a cooking class to learn Italian cuisine",
"spending the afternoon painting a landscape with watercolors",
"going to a local arcade to play retro video games",
"joining a dance class to learn salsa or tango"],   
]

with open (args.gpt4_output,'r') as f:
    char_actions_qa_data=json.load(f)
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

character_actions_qa=[]   
for key_name in char_actions_qa_data:
    # grey_season_03_episode_23
    name_list=key_name.split('_')
    show_name=name_list[0]
    season="season_"+name_list[2]
    episode="episode_"+name_list[4]
    for qa in char_actions_qa_data[key_name]:
        question=MCQ_header+qa['Q']
        correct_answer=qa['A'].copy() # list of actions
        # create a list of wrong answers 
        options=generate_unique_options(correct_answer)
        options.append(correct_answer)
        # add I don't know option 
        options.append("I don't know")
        # shuffle the options 
        random.shuffle(options)
        answer_key=options.index(correct_answer)
        data={}
        data['answer_idx']=answer_key
        data['options']=options
        data['question']=question
        data['season']=season
        data['episode']=episode
        data['show']=show_name
        data['video_path']=f"/{show_name}/{season}/{episode}.mp4"
        data['video_path_frames']=f"/{show_name}/{season}/{episode}"
        data['video_subtitles'] = f"{show_name}/{season}/{episode}.srt"
        character_actions_qa.append(data)
        
os.makedirs("../../benchmark",exist_ok=True)  
with open ('../../benchmark/tvqa_character_actions.json','w') as f:
    json.dump(character_actions_qa,f,indent=4)
    
    
    
    
    