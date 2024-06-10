import os 
import json
import argparse
parser = argparse.ArgumentParser('filter movienet')
parser.add_argument('--movienet_path', type=str,default="", help="path to the movienet movies frames")

args = parser.parse_args()

movies_has_subtitles=json.load(open("movies_has_subtitles.json",'r'))
path =args.movienet_path
for movie_name in os.listdir(path):
    if not movies_has_subtitles.get(movie_name,False):
        print(movie_name)
        os.system(f"rm -r {os.path.join(path,movie_name)}")
        print(f"Removed {movie_name} from {path}")