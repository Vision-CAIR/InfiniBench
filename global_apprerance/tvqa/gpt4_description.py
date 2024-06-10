
import base64
import requests
import os
from openai import OpenAI
import json
import time
import ast
from tqdm import tqdm
import argparse
# add path to the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--data_path", type=str, default="character_cropped_images_filtered_humanly")
parser.add_argument("--output_dir", type=str, default="GPT4o_output")
parser.add_argument("--api_key", required=True)

args = parser.parse_args()
data_path = args.data_path
output_dir = args.output_dir

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')





headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {args.api_key}"
}

def prepare_the_payload(image_paths):
    # Getting the base64 string
    encoded_images = [encode_image(image_path) for image_path in image_paths]
    content = [
        {
            "type": "text",
            "text": "I will provide you a sequence of images, your task is to describe the changing in outfits in these images.\n"
                    "Your output should be a python list of the changes in the outfits in the images.\n"
        }
    ]

    for base64_image in encoded_images:
        image_data = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
            },
        }
        content.append(image_data)

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "##TASK: Users will provide a sequence of images. Your task is to describe in detail the changing in outfits in these images.\n"
                                "Your output should be a python list of the changes in the outfits in the images.\n"
                                "##One shot samples\n"
                                "image 1 base64, image 2 base64, ..., image n base64\n"
                                "The response should be ONLY python list like this without any explainations: ['red t-shirt under a beige jacket with a green hood', 'black leather jacket', ...] ensuring that the sequence of changes is ordered as the first image then the second image then the third image and so on.\n"
                    }
                ]
            },
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 300,
    }
    return payload


global_appreance_data={}
number_of_requests=0
for season in tqdm (sorted(os.listdir(data_path)), desc="Seasons"):
  if os.path.exists(f'{output_dir}/{season}_appreance.json'):
    with open(f'{output_dir}/{season}_appreance.json', 'r') as f:
      season_global_appreance_data = json.load(f)
  else:
    season_global_appreance_data={}
  for episode in tqdm(os.listdir(os.path.join(data_path,season)), desc="Episodes"):
    for character in os.listdir(os.path.join(data_path,season,episode)):
      # if season and episode and character already processed skip it
      if season in season_global_appreance_data and episode in season_global_appreance_data[season] and character in season_global_appreance_data[season][episode]:
        print(f"Skipping '{season}_{episode}_{character}'")
        continue
      image_paths=[]
      for image in sorted(os.listdir(os.path.join(data_path,season,episode,character))):
        image_path=os.path.join(data_path,season,episode,character,image)
        image_paths.append(image_path)
        
      payload=prepare_the_payload(image_paths)
      # print(image_paths)
      done=False
      while not done:
        try:
          response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
          number_of_requests+=1
          if season not in global_appreance_data:
            global_appreance_data[season]={}
          if season not in season_global_appreance_data:
            season_global_appreance_data[season]={} 
          if episode not in global_appreance_data[season]:
            global_appreance_data[season][episode]={}
          if episode not in season_global_appreance_data[season]:
            season_global_appreance_data[season][episode]={}
          output_text=response.json()['choices'][0]['message']['content']
          try:
            output_list=ast.literal_eval(output_text)
            global_appreance_data[season][episode][character]=output_list
            season_global_appreance_data[season][episode][character]=output_list
          except:
            print("output can't be converted to list")
            global_appreance_data[season][episode][character]=output_text
            season_global_appreance_data[season][episode][character]=output_list
          done=True
        except Exception as e:
          print(f"Error processing '{season}_{episode}_{character}': {e}")
          time.sleep(5)
  
      with open(f'{output_dir}/{season}_appreance.json', 'w') as f:
        json.dump(season_global_appreance_data, f)

with open(f'{output_dir}/global_appreance.json', 'w') as f:
    json.dump(global_appreance_data, f)

print(f"Number of requests: {number_of_requests}")