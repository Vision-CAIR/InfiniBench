import json 
import os 
import re 
from tqdm import tqdm

import shutil
import argparse
# add --val path and the --train path to the script arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--val_path', type=str,default="/ibex/project/c2090/datasets/TVR_dataset/tvqa_qa_release/tvqa_val.jsonl" ,help='path to the val json file')
parser.add_argument('--train_path', type=str,default="/ibex/project/c2090/datasets/TVR_dataset/tvqa_qa_release/tvqa_train.jsonl", help='path to the train json file')

parser.add_argument('--root_dir', type=str,default="/ibex/project/c2090/datasets/TVR_dataset/videos/video_files/frames_hq/", help='path to the clips frames directory')
parser.add_argument('--full_videos_dir', type=str,default="/ibex/project/c2106/kirolos/Long_TVQA/videos", help='path to save the full episodes frames')

args = parser.parse_args()

def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Load each line as a JSON object
            json_data = json.loads(line.strip())
            data.append(json_data)
    return data
def extract_season_episode(video_name):
    # Define a regex pattern to match season and episode numbers
    pattern = r's(\d+)e(\d+)'

    # Use re.search to find the pattern in the video name
    match = re.search(pattern, video_name, re.IGNORECASE)

    if match:
        # Extract season and episode numbers from the matched groups
        season_number = int(match.group(1))
        episode_number = int(match.group(2))
        return f"season_{season_number}", f"episode_{episode_number}"
    else:
        # Return None if the pattern is not found
        return None, None

val_data=read_jsonl(args.val_path)
train_data=read_jsonl(args.train_path)

# generate the full TVQA long episodes 
tv_shows_full_data={}
for data in [val_data,train_data]:
    for d in tqdm(data) :
        # collect the related question to each the episode
        # extrct the season and episode numbers from the video name 
        season, episode = extract_season_episode(d['vid_name'])
        
        if d['show_name'] not in tv_shows_full_data:
            tv_shows_full_data[d['show_name']]={}
        if season not in tv_shows_full_data[d['show_name']]:
            tv_shows_full_data[d['show_name']][season]={}
        if episode not in tv_shows_full_data[d['show_name']][season]:
            tv_shows_full_data[d['show_name']][season][episode]={} 

mapping={"Grey's Anatomy":"grey_frames", 'How I Met You Mother':"met_frames", 'Friends':"friends_frames", 'The Big Bang Theory':"bbt_frames", 'House M.D.':"house_frames", 'Castle':"castle_frames"} 
root_dir=args.root_dir
full_videos_dir=args.full_videos_dir
os.makedirs(full_videos_dir,exist_ok=True)       

number_of_episodes=0
for show in tqdm(tv_shows_full_data,desc="shows"):
    os.makedirs(os.path.join(full_videos_dir,mapping[show]),exist_ok=True)
    for season in tqdm(tv_shows_full_data[show],desc="seasons"):
        os.makedirs(os.path.join(full_videos_dir,mapping[show],season),exist_ok=True)
        for episode in tqdm(tv_shows_full_data[show][season],desc="episodes"):
            episode_path=os.path.join(full_videos_dir,mapping[show],season,episode)
            os.makedirs(episode_path,exist_ok=True)
            all_frames_dir=os.path.join(root_dir,mapping[show])
            # each episode is segmented into parts and each part is segmented into clips , we need to collect all the clips of the episode 
            # and merge them into one video
            # collect all the clips of the episode
            # get all folders which match this pattern s{season}e{episode}
            s=season.split('_')[1].zfill(2)
            e=episode.split('_')[1].zfill(2)
            pattern = f's{s}e{e}'
            # print(pattern)
            folders_list = [f for f in os.listdir(all_frames_dir) if re.search(pattern, f, re.IGNORECASE)]
            sorted_folders_list=sorted(folders_list)
            tv_shows_full_data[show][season][episode]['clips']=sorted_folders_list
            number_of_episodes+=1
            # create the full episode by merging all the clips images
            frame_number=0
            for folder in sorted_folders_list:
                # get all the frames of the folder
                folder_path=os.path.join(all_frames_dir,folder)
                for frame in sorted(os.listdir(folder_path)):
                    frame_path=os.path.join(folder_path,frame)
                    new_frame_name=str(frame_number).zfill(5)+".jpg"
                    shutil.copy(frame_path,os.path.join(episode_path,new_frame_name))
                    frame_number+=1

print("Total number of Long episodes in TVQA for both Training and validation :",number_of_episodes)
tv_shows_val={}
for d in tqdm(val_data) :
    # collect the related question to each the episode
    # extrct the season and episode numbers from the video name 
    season, episode = extract_season_episode(d['vid_name'])
    
    if d['show_name'] not in tv_shows_val:
        tv_shows_val[d['show_name']]={}
    if season not in tv_shows_val[d['show_name']]:
        tv_shows_val[d['show_name']][season]={}
    if episode not in tv_shows_val[d['show_name']][season]:
        tv_shows_val[d['show_name']][season][episode]={} 

            
    tv_shows_val[d['show_name']][season][episode]['questions']=[]


for d in tqdm(val_data) :
    # collect the related question to each the episode
    # qa_pair=[{'question':d['q'],'a0':d['a0'],'a1':d['a1'],'a2':d['a2'],'a3':d['a3'],'a4':d['a4'],"answer_idx":d['answer_idx']}]
    season, episode = extract_season_episode(d['vid_name'])
    tv_shows_val[d['show_name']][season][episode]['questions'].append(d)
        
# save the data in json format 
with open('tvqa_val_edited.json', 'w') as fp:
    json.dump(tv_shows_val, fp)

number_of_clips=0
number_of_episodes=0
number_of_questions=0
number_of_questions_in_episode=[]
for show in tqdm(tv_shows_val,desc="shows"):
    os.makedirs(os.path.join(full_videos_dir,mapping[show]),exist_ok=True)
    for season in tqdm(tv_shows_val[show],desc="seasons"):
        os.makedirs(os.path.join(full_videos_dir,mapping[show],season),exist_ok=True)
        for episode in tqdm(tv_shows_val[show][season],desc="episodes"):
            episode_path=os.path.join(full_videos_dir,mapping[show],season,episode)
            os.makedirs(episode_path,exist_ok=True)
            all_frames_dir=os.path.join(root_dir,mapping[show])
            # each episode is segmented into parts and each part is segmented into clips , we need to collect all the clips of the episode 
            # and merge them into one video
            # collect all the clips of the episode
            # get all folders which match this pattern s{season}e{episode}
            s=season.split('_')[1].zfill(2)
            e=episode.split('_')[1].zfill(2)
            pattern = f's{s}e{e}'
            # print(pattern)
            folders_list = [f for f in os.listdir(all_frames_dir) if re.search(pattern, f, re.IGNORECASE)]
            sorted_folders_list=sorted(folders_list)
            tv_shows_val[show][season][episode]['clips']=sorted_folders_list
            number_of_clips+=len(sorted_folders_list)
            number_of_questions+=len(tv_shows_val[show][season][episode]['questions'])
            number_of_questions_in_episode.append(len(tv_shows_val[show][season][episode]['questions']))
            number_of_episodes+=1

print("number of clips",number_of_clips)
print("number of episodes",number_of_episodes)
print("number of questions",number_of_questions)
assert len(number_of_questions_in_episode)==number_of_episodes
print("Average number of questions in episode",sum(number_of_questions_in_episode)/len(number_of_questions_in_episode))
print("max number of questions in episode",max(number_of_questions_in_episode))
print("min number of questions in episode",min(number_of_questions_in_episode))
with open('tvqa_val_edited.json', 'w') as fp:
    json.dump(tv_shows_val, fp)



         
   