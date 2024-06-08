import os 
import json 

data=json.load(open('imdb_summaries.json', 'r'))
txt_sumaries_folder='summaries_txt'
os.makedirs(txt_sumaries_folder, exist_ok=True)
for show in data:
    for season in data[show]:
        for episode in data[show][season]:
            summary=data[show][season][episode]
            with open(f'{txt_sumaries_folder}/{show}_{season}_{episode}.txt', 'w') as f:
                f.write(summary)