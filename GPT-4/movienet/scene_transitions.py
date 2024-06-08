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
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="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",
)

def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-4")
    parser.add_argument("--gt_caption_folder", default='summ_copy')
    parser.add_argument("--output_dir", default='scene_transition_without_brackets')
    parser.add_argument("--output_json", default="scene_transition_without_brackets.json")
    parser.add_argument("--api_key",default="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")
    parser.add_argument("--num_tasks", default=3, type=int)
    args = parser.parse_args()
    return args


def read_subtitles(subtitle_path):
    # read the subtitle file and detect the encoding
    try:
        with open(subtitle_path, 'rb') as f:
            result = chardet.detect(f.read())
        subs = pysrt.open(subtitle_path, encoding=result['encoding']) 
        return subs
    except:
        return []

     
def annotate(gt_file, caption_files, output_dir):
    """
    Generate questions and answers for each caption file using GPT-3.
    """
    for file in caption_files:
        key = file[:-5] # Strip file extension.
        caption = gt_file[key]
        try:
            # Generate gpt-4o response.
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": 
                            "##TASK: "
                            "Users will provide a Movie Screenplay Script. Your task is to extract scene transitions in this movie.\n"
                            "First read the Screenplay script and think carefully to extract the transitions between scenes.\n"
                            "------\n"
                            "##Few shot samples\n"
                            "Movie Screenplay Script: {user Screenplay Script}\n"
                            "Extract the scene transitions from this Movie Screenplay Script:\n"
                            "The response should be in the format: ['scene A name', 'scene B name', 'scene C name',...], ensuring that the squenece of transitions is ordered as scene A then scene B then scene C and so on.\n" 
                            "please provide the response in the format of python list of scene transitions like this example : ['scene A name', 'scene B name', 'scene C name',...], ensuring that the scene changed from A to B then C and so on.\n" 
                            "Remember well the output format of ONLY a python list of events and DON'T output the python shell because I will use python ast library to parse your output list.\n"

                    },
                    {
                        "role":"user",
                        "content":
                            f"Movie Screenplay Script: {caption}\n"
                            "Extract the scene transitions from this Screenplay Script in a list\n"
                            "please provide the response in the format of python list of scene transitions like this example : ['scene A name', 'scene B name', 'scene C name',...], ensuring that the scene changed from A to B then C and so on.\n" 
                            "DON'T output any other informations because I will parse your output list.\n"

                    }

                ]
            )
            # Convert response to a Python dictionary.
            print("input tokens: ", completion.usage.prompt_tokens)
            print("output tokens: ", completion.usage.completion_tokens)
            print("total tokens: ", completion.usage.total_tokens)
            response_message = completion.choices[0].message.content
            response_dict = ast.literal_eval(response_message)

            # Save the question-answer pairs to a json file.
            with open(f"{output_dir}/{key}.json", "w") as f:
                json.dump(response_dict, f)
            with open(f"events_txt/{key}.txt", "w") as f:
                json.dump(response_dict, f)
        except Exception as e:
            print(f"Error processing file '{key}': {e}")
            print(f"response: {response_message}")


def main():
    """
    Main function to control the flow of the program.
    """
    # Parse arguments.
    args = parse_args()

    # Read ground truth captions.
    gt_captions = {}
    gt_files = os.listdir(args.gt_caption_folder)
    for file in gt_files:
        with open(os.path.join(args.gt_caption_folder, file), mode='r', encoding='utf-8-sig') as f:
            caption = f.read().replace('\n', '').replace('‘', "'").replace('’', "'")
            video_id = file[:-7]
            gt_captions[video_id] = caption

    caption_files = [f"{video_id}.json" for video_id in gt_captions.keys()]
    output_dir = args.output_dir
    # Generate output directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    num_tasks = args.num_tasks

    # While loop to ensure that all captions are processed.
    while True:
        try:
            # Files that have not been processed yet.
            completed_files = os.listdir(output_dir)
            print(f"completed_files: {len(completed_files)}")

            # Files that have not been processed yet.
            incomplete_files = [f for f in caption_files if f not in completed_files]
            print(f"incomplete_files: {len(incomplete_files)}")

            if len(incomplete_files) == 0:
                break
            if len(incomplete_files) <= num_tasks:
                num_tasks = 1

            # Split tasks into parts.
            part_len = len(incomplete_files) // num_tasks
            all_parts = [incomplete_files[i:i + part_len] for i in range(0, len(incomplete_files), part_len)]
            task_args = [(gt_captions, part, args.output_dir) for part in all_parts]

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
