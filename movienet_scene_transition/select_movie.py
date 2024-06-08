import os 
import json 
import random 

with open ('places_transitions.json','r') as f :
    places_transitions=json.load(f)

# movie_idx =random.randint(111) 
movie_idx=20
movies=list(places_transitions.keys())
base_url="https://www.imdb.com/title/"
for movie in movies: 
    url=base_url+movie 
    print(url)