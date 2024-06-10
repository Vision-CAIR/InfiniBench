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
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-4")
    parser.add_argument("--summaries_folder", default='path to the folder containing the episodes summaries')
    parser.add_argument("--scripts_folder", default='path to the folder containing episodes Screenplay Scripts')
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


def annotate(gt_file, caption_files, output_dir):
    """
    Generate questions and answers for each caption file using GPT-3.
    """
    for file in tqdm(caption_files):
        key = file[:-5] # Strip file extension.
        summary = gt_file[key]
        # Generate GPT-4o response.
        completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": 
                    "You play two roles: a human asking questions related to a video and an intelligent chatbot designed to help people find information from a given video. "
                    "Your task is to generate question-answer pairs specifically related to linking multiple events in the video content. "
                    "You will first play the role of a human who asks questions that link multiple events together in the video, and then play the role of an AI assistant that provides information based on the video content."
                    "------"
                    "##TASK: "
                    "Users will provide information about the video, and you will generate a conversation-like question and answer pairs specifically focusing on linking multiple events together in the video to make the questions comprehensive across the video. "
                    "Generate up to TWENTY descriptive and conversational-style questions and their detailed answers based on the given information, specifically related to linking multiple events together in the video. "
                    "------"
                    "##INSTRUCTIONS:"
                    "- The questions must be conversational, as if a human is asking them, and should directly relate to linking multiple events together in the video. "
                    "- The answers must be detailed, descriptive, and should directly reference the information provided."
                    "- The number of events to link together can vary from 2 to any number of events. "
                    "Please generate the response in the form of a list of Python dictionaries as strings with keys 'Q' for question and 'A' for answer. Each corresponding value should be the question and answer text respectively. "
                    "For example, your response should look like this: [{\"Q\": \"Your question here...\", \"A\": \"Your answer here...\"},{\"Q\": \"Your question here...\", \"A\": \"Your answer here...\"}]"
                    "Make sure to avoid to put double quotes inside string with double quotes, use single quotes instead. For example, use \"I drived 'John's car' yesterday\" instead of 'I drived \"John's car\" yesterday' ."
                    "please only output the required format, do not include any additional information."
                    "Remember well the output format of ONLY a PYTHON LIST as output and DON'T output the python shell because I will use python ast library to parse your output list.\n"

                    "## Few shot examples about the questions:"
                    "- What is the influence of event A on event B?"
                    "- How does event A lead to event B?"
                    "- What is the relationship between event A and event B?"
                    "- What is the impact of event A on event B?"
                    "- How does event A affect event B?"
                    "- What is the connection between event A, event B, and event C?"
            },
            {
                "role": "user",
                "content":
                    f"The user input is: {summary}. "
                    "Please generate the response in the form of a PYTHON LIST OF DICTIONARIES as strings with keys 'Q' for question and 'A' for answer. Each corresponding value should be the question and answer text respectively. "
                    "For example, your response should look like this: [{\"Q\": \"Your question here...\", \"A\": \"Your answer here...\"},{\"Q\": \"Your question here...\", \"A\": \"Your answer here...\"}]"
                    "DON'T output any other informations because I will parse your output list.\n"
            }
        ]
    )

        # Convert response to a Python dictionary.
        response_message = completion.choices[0].message.content
        try:
            response_dict = ast.literal_eval(response_message)
        except:
            print("cannot parse response")
            response_dict = response_message

        # Save the question-answer pairs to a json file.
        with open(f"{output_dir}/{key}.json", "w") as f:
            json.dump(response_dict, f)
def main():
    """
    Main function to control the flow of the program.
    """

    # Read ground truth captions.
    gt_captions = {}
    gt_files = os.listdir(args.summaries_folder)
    for file in gt_files:
        with open(os.path.join(args.summaries_folder, file), mode='r', encoding='utf-8-sig') as f:
            caption = f.read().replace('\n', '').replace('‘', "'").replace('’', "'")
            video_id = file[:-4]
            gt_captions[video_id] = caption

    caption_files = [f"{video_id}.json" for video_id in gt_captions.keys()]
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
