import os 
import json

for season in os.listdir('character_cropped_images_long'):
    for episode in os.listdir(os.path.join('character_cropped_images_long',season)):
        for character in os.listdir(os.path.join('character_cropped_images_long',season,episode)):
            if len (os.listdir(os.path.join('character_cropped_images_long',season,episode,character)))<2:
                os.system(f"rm -r {os.path.join('character_cropped_images_long',season,episode,character)}")