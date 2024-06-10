import openai
import os
import argparse
import warnings
import json
import ast
from multiprocessing.pool import Pool

warnings.filterwarnings('ignore')
import pysrt
import chardet
from tqdm import tqdm

from openai import OpenAI

def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-4")
    parser.add_argument("--scripts_folder", default='path to the folder containing movies Screenplay Scripts')
    parser.add_argument("--output_dir", default='path to the folder where the output json files will be saved')
    parser.add_argument("--output_json", default="path to the output json file where all the qa pairs will be saved")
    parser.add_argument("--api_key",required=True)
    parser.add_argument("--num_tasks", default=32, type=int)
    args = parser.parse_args()
    return args

# Parse arguments.
args = parse_args()
client = OpenAI(
    # This is the default and can be omitted
    api_key=args.api_key
)

def read_subtitles(subtitle_path):
    # read the subtitle file and detect the encoding
    try:
        with open(subtitle_path, 'rb') as f:
            result = chardet.detect(f.read())
        subs = pysrt.open(subtitle_path, encoding=result['encoding']) 
        return subs
    except:
        return []

     
def annotate(gt_file, scripts_files, output_dir):
    """
    Generate questions and answers for each caption file using GPT-4o.
    """
    for file in tqdm(scripts_files):
        key = file[:-5] # Strip file extension.
        script = gt_file[key]
        if key =="tt0408790":
            with open(f"{output_dir}/{key}.json", "w") as f:
                json.dump({}, f)
            continue
        # Generate gpt-4o response.
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": 
                        "##TASK: "
                        "Users will provide an episode Screenplay Script. Your task is to extract the events from this Screenplay Script.\n Ensure that the events are listed in chronological order"
                        "First read the Screenplay Script and think carefully to extract the all events.\n"
                        "-Make sure to avoid to put double quotes inside string with double quotes, use single quotes instead. For example, use \"I drived 'John's car' yesterday\" instead of 'I drived \"John's car\" yesterday' ."
                        "-please only output the required format, do not include any additional information."
                        "-Remember well the output format of ONLY a PYTHON LIST as output\n"

                        "------\n"
                        "##Few shot samples\n"
                        "Episode Screenplay Script: {user Screenplay Script}\n"
                        "Extract the events from this episode Screenplay Script:\n"
                        "The response should be in the format: [\"Event A\", \"Event B\", \"Event C\", \"Event D\",...], ensuring that the event B is after event A and before Event C.\n" 
                        "Remember well the output format of ONLY a PYTHON LIST of events and DON'T output the python shell because I will use python ast library to parse your output list.\n"

                },
                {
                    "role":"user",
                    "content":
                        f"Episode Screenplay Script: {script}\n"
                        "Extract the events from the Screenplay Script in a list\n"
                        "please provide the response in the format of PYTHON LIST of DON'T output any other informations because I will parse your output list.\n"
                        "DON't output any ’ or ' in your response but use /u2019 for ’ and /u2019s for ’s and /u2019t for ’t and s/u2019 for s' or s’ \n"
                }

            ]
        )
        # Convert response to a Python dictionary.
        response_message = completion.choices[0].message.content
        response_message=response_message.replace("’","'")
        response_message = response_message.replace("'s ", "\u2019s ")  
        response_message = response_message.replace("s' ", "s\u2019 ")   
        response_message = response_message.replace("'t ", "\u2019t ")    
        response_message = response_message.replace("```python", "")
        response_message = response_message.replace("```", "")
        # replace double quotes with single quotes
        try:          
            response_dict = ast.literal_eval(response_message)
        except:
            print(key,"output can't be parsed")
            response_dict = response_message

        # Save the question-answer pairs to a json file.
        with open(f"{output_dir}/{key}.json", "w") as f:
            json.dump(response_dict, f)
        
            


def main():
    """
    Main function to control the flow of the program.
    """

    # Read ground truth captions.
    scripts = {}
    scripts_files_list = os.listdir(args.scripts_folder)
    for file in scripts_files_list:
        with open(os.path.join(args.scripts_folder, file), mode='r', encoding='utf-8-sig') as f:
            caption = f.read().replace('‘', "'").replace('’', "'")
            video_id = file[:-4]
            scripts[video_id] = caption

    scripts_files = [f"{video_id}.json" for video_id in scripts.keys()]
    output_dir = args.output_dir
    # Generate output directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set the OpenAI API key.
    openai.api_key = args.api_key
    num_tasks = args.num_tasks

    # While loop to ensure that all captions are processed.
    while True:
        try:
            # Files that have not been processed yet.
            completed_files = os.listdir(output_dir)
            print(f"completed_files: {len(completed_files)}")

            # Files that have not been processed yet.
            incomplete_files = [f for f in scripts_files if f not in completed_files]
            print(f"incomplete_files: {len(incomplete_files)}")

            if len(incomplete_files) == 0:
                break
            if len(incomplete_files) <= num_tasks:
                num_tasks = 1

            # Split tasks into parts.
            part_len = len(incomplete_files) // num_tasks
            all_parts = [incomplete_files[i:i + part_len] for i in range(0, len(incomplete_files), part_len)]
            task_args = [(scripts, part, args.output_dir) for part in all_parts]

            # Use a pool of workers to process the files in parallel.
            with Pool() as pool:
                pool.starmap(annotate, task_args)

        except Exception as e:
            print(f"Error: {e}")

    # Combine qa pairs into single file when individual qa generation completes
    all_data = {}
    for filename in os.listdir(output_dir):
        if filename.endswith(".json"):
            with open(os.path.join(output_dir, filename)) as f:
                key = filename[:-5]
                all_data[key] = json.load(f)

    with open(args.output_json, 'w') as f:
        json.dump(all_data, f, indent=4)


if __name__ == "__main__":
    main()
