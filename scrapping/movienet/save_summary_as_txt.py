import os 
import json 

data=json.load(open('movienet_summaries.json', 'r'))
txt_sumaries_folder='summaries_txt'
os.makedirs(txt_sumaries_folder, exist_ok=True)
for movie in data:
    summary=data[movie]
    with open(f'{txt_sumaries_folder}/{movie}.txt', 'w') as f:
        f.write(summary)