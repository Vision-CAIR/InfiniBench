import json 
import random
import os

data=json.load(open('filtered_fqa_questions_answers.json','r'))
for movie in data:
    data[movie]['video_path_mp4']=f"/{movie}.mp4"
    data[movie]['video_path_frames']=f"/{movie}"
    data[movie]['video_subtitles']=f"/{movie}.srt"
    data[movie]['name']=movie
    
os.makedirs("../../benchmark",exist_ok=True)
with open("../../benchmark/movies_spoiler_questions.json",'w') as f:
    json.dump(data,f,indent=4)