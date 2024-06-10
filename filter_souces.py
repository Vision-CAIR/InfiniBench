import os 
import json
existed_episodes=json.load(open("existed_videos_tvqa.json",'r'))
movies_has_subtitles=json.load(open("movies_has_subtitles.json",'r'))
path ="sources_filtered/scripts"
for folder in os.listdir(path):
    if folder == "movienet_scripts":
        for script_name in os.listdir(os.path.join(path,folder)):
            movie_name= script_name.split(".")[0]
            if not movies_has_subtitles.get(movie_name,False):
                print(movie_name)
                os.remove(os.path.join(path,folder,script_name))
                print(f"Removed {movie_name} from {folder}")
    else:
        for script_name in os.listdir(os.path.join(path,folder)):
            show_name= script_name.split("_")[0]
            season_number = int(script_name.split("_")[2])
            episode_number = int(script_name.split("_")[4].split(".")[0])
            episode_name = f"{show_name}_season_{season_number}_episode_{episode_number}"
            if f"/{show_name}/season_{season_number}/episode_{episode_number}" not in existed_episodes:
                print(episode_name)
                os.remove(os.path.join(path,folder,script_name))
                print(f"Removed {episode_name} from {folder}")