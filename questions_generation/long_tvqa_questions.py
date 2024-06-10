import os 
import json 

import argparse
parser = argparse.ArgumentParser(description="question-answer-generation")
parser.add_argument("--tvqa_val_edited",required=True, help="Path to the edited TVQA validation data")

args = parser.parse_args()

tvqa_val_data =json.load(open(args.tvqa_val_edited, 'r'))
mapping={"Grey's Anatomy":"grey", 'How I Met You Mother':"met", 'Friends':"friends", 'The Big Bang Theory':"bbt", 'House M.D.':"house", 'Castle':"castle"} 
MCQ_header="Choose the correct option for the following question: "
long_tvqa_data=[]
for show in tvqa_val_data:
    for season in tvqa_val_data[show]:
        for episode in tvqa_val_data[show][season]:
            show_name=mapping[show]
            video_path=f"/{show_name}/{season}/{episode}"
            # print(data[show][season][episode].keys())
            qa_list=tvqa_val_data[show][season][episode]['questions']
            for qa in qa_list:
                question=MCQ_header+qa['q']
                answe_idx=qa['answer_idx']
                options=[]
                for i in range(5):
                    options.append(qa[f"a{i}"])
                data={}
                data['question']=question
                data['video_path_mp4']=video_path+'.mp4'
                data['video_path_frames']=video_path
                data['video_subtitles']=video_path+'.srt'   
                data['answer_idx']=answe_idx
                data['options']=options
                data['season']=season
                data['episode']=episode
                data['show']=show_name
                        
                long_tvqa_data.append(data)
                
with open('../benchmark/final/long_tvqa_questions.json','w') as f:
    json.dump(long_tvqa_data,f,indent=4)