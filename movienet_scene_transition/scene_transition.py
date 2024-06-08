import os 
import json
import shutil
movies_path="/ibex/reference/videos/MoiveNet/images"
existed_movies={}
for movie in os.listdir(movies_path):
    existed_movies[movie]=True
# ann_path="/ibex/reference/videos/MoiveNet/MovieNet/raw/files/annotation"
# number_of_movies_has_scene_transitions=0
# os.makedirs('annotations',exist_ok=True)
# for file in os.listdir(ann_path):
#     movie_name=file.split(".")[0]
#     if existed_movies.get(movie_name,False):
#         with open(os.path.join(ann_path,file),'r') as f:
#             data=json.load(f)
#             if data['scene']:
#                 number_of_movies_has_scene_transitions+=1
#                 shutil.copy(os.path.join(ann_path,file),f'annotations/{file}')

# print(f"number of movies has scene transitions {number_of_movies_has_scene_transitions}")
transitions=[]
places_transitions={}
for movie in os.listdir('annotations'):
    movie_name=movie.split('.')[0]
    places_transitions[movie_name]=[]
    with open(f'annotations/{movie}','r') as f:
        data=json.load(f)
        for scene in data['scene']:
            if scene['place_tag']:
                places_transitions[movie_name].append(scene['place_tag'])
        transitions.append(len(data['scene']))
    if len(places_transitions[movie_name])==0:
        places_transitions.pop(movie_name)
        
print(f"average number of scene transitions {sum(transitions)/len(transitions)}")
print(f"max number of scene transitions {max(transitions)}")
print(f"min number of scene transitions {min(transitions)}")
print(f"number of movies {len(transitions)}")
print(f"Number of movies that have places transitions {len(places_transitions)}")
with open('places_transitions.json','w') as f:
    json.dump(places_transitions,f)
