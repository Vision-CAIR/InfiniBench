import os 
import json 
import ast
path='season_{}_appreance.json'
full_data={}
for i in range(1,11):
    path='season_{}_appreance.json'.format(i)
    if os.path.exists(path):
        data = json.load(open(path))
        for season in data:
            for episode in data[season]:
                for character in data[season][episode]:
                    outfit=data[season][episode][character]
                    # check if the outfit is a list
                    if not isinstance(outfit, list):
                        print(outfit)

        full_data.update(data)
        
print(len(full_data))
for season in full_data:
    for episode in full_data[season]:
        for character in full_data[season][episode]:
            outfit=full_data[season][episode][character]
            # check if the outfit is a list
            if not isinstance(outfit, list):
                print(outfit)
with open('global_appreance.json', 'w') as f:
    json.dump(full_data, f)

