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
pool_of_questions=[
    "what is the correct squence of events that happened in this movie?",
    "Can you list the events in the order they occurred in this movie?",
    "How did the events unfold in this movie?",
    "What is the chronological order of events in this movie?",
    "Could you arrange the events of this movie in sequence?",
    "What happened first, second, and so on in this movie?",
    "What is the timeline of events in this movie?",
    "How did the storyline progress in this movie?",
    "Could you list the scenes in the order they occur in this movie?",
    "Could you outline the sequence of events in this movie?",
]
pool_for_sub_events=[
    "Given these events {} that happened in this movie, what is the correct sequence of events?",
    "Based on these events {} from the movie, what is the order they occurred in?",
    "With these events in mind {}, how should they be sequenced in this movie?",
    "Considering these events {}, what is their chronological order in the movie?",
    "Given these happenings {}, what is the correct order in which they occurred in the movie?",
    "Looking at these events {}, how do they unfold in the movie?",
    "With the provided events {}, what is their correct order in the movie?",
    "Given the events listed {}, what is the sequential order in this movie?",
]


with open (args.gpt4_output,'r') as f:
    events_data=json.load(f)

def create_yes_no_qa (event_1,event_2,movie_name):
    question1=f"Did the event '{event_1}' happen before the event '{event_2}'?" # A1:Yes
    question2=f"Did the event '{event_2}' happen before the event '{event_1}'?"# A2:No
    question3=f"Did the event '{event_1}' happen after the event '{event_2}'?" # A1:NO
    question4=f"Did the event '{event_2}' happen after the event '{event_1}'?" # A2:Yes
    data1={}
    data2={}
    data3={}
    data4={}
    data1['question']=question1
    data2['question']=question2
    data3['question']=question3
    data4['question']=question4
    data1['movie_name']=movie_name
    data2['movie_name']=movie_name
    data3['movie_name']=movie_name
    data4['movie_name']=movie_name
    data1['video_path_mp4']=f"/{movie_name}.mp4"
    data2['video_path_mp4']=f"/{movie_name}.mp4"
    data3['video_path_mp4']=f"/{movie_name}.mp4"
    data4['video_path_mp4']=f"/{movie_name}.mp4"
    data1['video_path_frames']=f"/{movie_name}"
    data2['video_path_frames']=f"/{movie_name}"
    data3['video_path_frames']=f"/{movie_name}"
    data4['video_path_frames']=f"/{movie_name}"
    data1['video_subtitles']=f"/{movie_name}.srt"
    data2['video_subtitles']=f"/{movie_name}.srt"
    data3['video_subtitles']=f"/{movie_name}.srt"
    data4['video_subtitles']=f"/{movie_name}.srt"
    data1['answer_idx']=0
    data2['answer_idx']=1
    data3['answer_idx']=1
    data4['answer_idx']=0
    data1['options']=['Yes','No']
    data2['options']=['Yes','No']
    data3['options']=['Yes','No']
    data4['options']=['Yes','No']
    return data1,data2,data3,data4
    
def generate_unique_options(correct_answer, num_options=4):
    # choose 4 random distractors without replacement
    all_events = correct_answer.copy()
    options=[]
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

temporal_questions=[]   
for movie_name in events_data:
    movie_events=events_data[movie_name]    
    correct_answer=movie_events.copy()
    if len(correct_answer)<3:
        continue
    # create a list of wrong answers 
    options=generate_unique_options(correct_answer)
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
    data['movie_name']=movie_name
    data['video_path_mp4']=f"/{movie_name}.mp4"
    data['video_path_frames']=f"/{movie_name}"
    data['video_subtitles']=f"/{movie_name}.srt"
    temporal_questions.append(data)
    #################################################################
    # loop over the events
    # for m in range(len(episode_events)-1) :
        # form 2 questions : q1 : Is event [m] happened before event [m+1]? A1:Yes , Is event [m+1] happened before event [m]? A2:No 
        # Is event [m+1] happened after event [m]? A1:Yes , Is event [m] happened after event [m+1]? A2:No 
        # the options are Yes and No 
    
    # for m in range(len(episode_events)-1):
    #     event1=episode_events[m]
    #     event2=episode_events[m+1]
    #     data1,data2,data3,data4=create_yes_no_qa(event1,event2,show_name,season,episode)
    #     temporal_questions.append(data1)
    #     temporal_questions.append(data2)
    #     temporal_questions.append(data3)
    #     temporal_questions.append(data4)
        
    # Not only ask about the adjacent events but also ask about any random 2 events 
    history_of_events={}
    for i in range(5):
        m=random.randint(0,len(movie_events)-1)
        n=random.randint(0,len(movie_events)-1)
        # m shouldn't be equal to n 
        while m==n:
            n=random.randint(0,len(movie_events)-1)
        # if the pair of events has been asked before, skip it
        l=sorted([m,n])
        if history_of_events.get(str(l),False):
            continue 
        history_of_events[str(l)]=True
        event1=movie_events[min(m,n)]
        event2=movie_events[max(m,n)]
        data1,data2,data3,data4=create_yes_no_qa(event1,event2,movie_name)
        temporal_questions.append(data1)
        temporal_questions.append(data2)
        temporal_questions.append(data3)
        temporal_questions.append(data4)
    
        
    # Ask questions about the correct sqeuence of some events say 3 or 4 events
    # first select 3 or 4 ordered events randomly  
    # shuffle the events 
    # form the question 
    # create the options
    # create the answer key
    history_of_events={}
    for i in range(3):
        for n in range(3,5):
            random_number=random.randint(0,len(movie_events)-n)
            l=range(random_number,random_number+n)
            if history_of_events.get(str(l),False):
                continue
            history_of_events[str(l)]=True
            selected_events=movie_events[random_number:random_number+n]
            correct_answer=selected_events.copy()
            options=generate_unique_options(correct_answer)
            options.append(correct_answer)
            # add I don't know option 
            options.append("I don't know")
            random.shuffle(selected_events)
            shuffled_events=selected_events.copy()
            random_q=random.choice(pool_for_sub_events).format(shuffled_events)
            question=f"{MCQ_header} {random_q}"
            random.shuffle(options)
            answer_key=options.index(correct_answer)
            data={}
            data['answer_idx']=answer_key
            data['options']=options
            data['question']=question
            data['movie_name']=movie_name
            data['video_path_mp4']=f"/{movie_name}.mp4"
            data['video_path_frames']=f"/{movie_name}"
            data['video_subtitles']=f"/{movie_name}.srt"
            temporal_questions.append(data)
        

os.makedirs("../../benchmark",exist_ok=True) 
with open ('../../benchmark/movienet_temporal_events.json','w') as f:
    json.dump(temporal_questions,f,indent=4)
    
    
    
    
    