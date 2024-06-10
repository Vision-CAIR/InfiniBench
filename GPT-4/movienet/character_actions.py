import openai
import os
import argparse
import warnings
import json
import ast
from multiprocessing.pool import Pool
from tqdm import tqdm
warnings.filterwarnings('ignore')
from openai import OpenAI

def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-4")
    parser.add_argument("--summaries_folder", default='../../sources/summaries/movienet_summaries')
    parser.add_argument("--scripts_folder", default='../../sources/scripts/movienet_scripts')
    parser.add_argument("--output_dir", default='../../skills_output/movienet/character_actions_qa')
    parser.add_argument("--output_json", default="../../skills_output/movienet/character_actions_qa.json")
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


def annotate(gt_file,gt_script, caption_files, output_dir):
    """
    Generate questions and answers for each caption file using GPT-3.
    """
    for file in tqdm(caption_files):
        key = file[:-5] # Strip file extension.
        caption = gt_file[key]
        script=gt_script[key]
        if key =="tt0408790":
            with open(f"{output_dir}/{key}.json", "w") as f:
                json.dump({}, f)
            continue
        # Generate GPT-4o response.
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": 
                        "You play two roles: a human asking questions related to a video and an intelligent chatbot designed to help people find information from a given video. "
                        "Your task is to generate a question-answer pairs specifically related to each character actions through the whole video content. "
                        "Your task is to first play the role of a human who asks questions about each character actions through the whole video content. and then play the role of an AI assistant that provides information based on the video content."
                        "------"
                        "##TASK: "
                        "Users will provide information about a video, and you will generate a conversation-like question and answers pair specifically focusing on each character actions through the whole video content. "
                        "Generate one question for each character that summariza all the actions did through the whole video content."
                        "------"
                        "##INSTRUCTIONS:"
                        "- The questions must be like a human conversation and directly related to each character actions through the whole video content. "
                        "- The answer must be detailed and descriptive that summarize all actions for each character in the video and should directly reference the information provided."
                        "- Focus on both the visual and texual actions but focus more on the vision actions as these questions are designed for video understanding."
                        "- The answer should be a list of actions in chronological order. "
                        "For example, your response should look like this: [{\"Q\": \"Your question here...\", \"A\": [\"Action 1\",\"Action 2\",...]},{\"Q\": \"Your question here\", \"A\": [\"Action 1\",\"Action 2\",...]}]. "
                        "-Make sure to avoid to put double quotes inside string with double quotes, use single quotes instead. For example, use \"I drived 'John's car' yesterday\" instead of 'I drived \"John's car\" yesterday' ."
                        "-please only output the required format, do not include any additional information."
                        "-Remember well the output format of ONLY a PYTHON LIST as output and DON'T output the python shell because I will use python ast library to parse your output list.\n"

                        "##SAMPLE QUESTIONS:"
                        "- {\"Q1\": \"What did ross do through this video?\",  \"A\": [\"At the begining of the episode he dranke cofffe in central park \",\" went to his apparment \",\"then ate some pizza.\"}"
                        "- {\"Q1\": \"Summarize all actions that chandler did in this video.\", \"A\": [\"At the begining of the episode he read a magazine \",\"went to his work by taxi \",\" and finally he went to monica's apparment to set with his friends.\"]}"
                },
                {
                    "role": "user",
                    "content":
                        f"This is the episode summary: {caption}. \n"
                        f"This is the episode script: {script}. \n"
                        "Please generate the response in the form of list of Python dictionaries string with keys 'Q' for question and 'A' for answer. Each corresponding value should be the question and answer text respectively. "
                        "For the answer please make it as a python list of actions in chronological order"
                        "For example, your response should look like this: [{\"Q\": \"Your question here...\", \"A\": [\"Action 1\",\"Action 2\",...]},{\"Q\": \"Your question here\", \"A\": [\"Action 1\",\"Action 2\",...]}]. "
                        "Please be very very accurate and detailed in your response. Thank you!"
                }
            ]
        )
        # Convert response to a Python dictionary.
        response_message = completion.choices[0].message.content
        try:
            response_dict = ast.literal_eval(response_message)
        except:
            response_dict=response_message

        # Save the question-answer pairs to a json file.
        with open(f"{output_dir}/{key}.json", "w") as f:
            json.dump(response_dict, f)

def main():
    """
    Main function to control the flow of the program.
    """
    # Read ground truth captions.
    gt_captions = {}
    gt_scripts= {}
    gt_files = sorted(os.listdir(args.summaries_folder))
    gt_script_files =sorted(os.listdir(args.scripts_folder))
    gt_files_new=[]
    for summ in gt_files:
        if summ not in gt_script_files:
            print("File not found in script folder: ", summ)
        else:
            gt_files_new.append(summ)
    gt_files=gt_files_new
            
    # scripts list has more files than captions list so we need to remove any script file that doesn't have a caption file
    filtered_scripts=[]
    for sc in gt_script_files:
        if sc in gt_files:
            filtered_scripts.append(sc)
    gt_script_files=filtered_scripts 
    gt_files.sort()
    gt_script_files.sort()
    print("len(gt_files): ", len(gt_files))
    print("len(gt_script_files): ", len(gt_script_files))
    for i in range(len(gt_files)):
        if gt_files[i]!=gt_script_files[i]:
            print("Mismatch: ", gt_files[i], gt_script_files[i])
    for file in gt_files:
        with open(os.path.join(args.summaries_folder, file), mode='r', encoding='utf-8-sig') as f:
            caption = f.read().replace('‘', "'").replace('’', "'")
            video_id = file[:-4]
            gt_captions[video_id] = caption
    
    for file in gt_script_files:
        with open(os.path.join(args.scripts_folder, file), mode='r', encoding='utf-8-sig') as f:
            script = f.read().replace('‘', "'").replace('’', "'")
            video_id = file[:-4]
            gt_scripts[video_id] = script

    caption_files = [f"{video_id}.json" for video_id in gt_captions.keys()]
    script_files = [f"{video_id}.json" for video_id in gt_scripts.keys()]
    output_dir = args.output_dir
    # Generate output directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set the OpenAI API key.
    num_tasks = args.num_tasks

    # While loop to ensure that all captions are processed.
    while True:
        # Files that have not been processed yet.
        completed_files = os.listdir(output_dir)
        print(f"completed_files: {len(completed_files)}")

        # Files that have not been processed yet.
        incomplete_files = [f for f in caption_files if f not in completed_files]
        print(f"incomplete_files: {len(incomplete_files)}")
        print(incomplete_files)

        if len(incomplete_files) == 0:
            break
        if len(incomplete_files) <= num_tasks:
            num_tasks = 1

        # Split tasks into parts.
        part_len = len(incomplete_files) // num_tasks
        all_parts = [incomplete_files[i:i + part_len] for i in range(0, len(incomplete_files), part_len)]
        task_args = [(gt_captions,gt_scripts, part, args.output_dir) for part in all_parts]

        # Use a pool of workers to process the files in parallel.
        with Pool() as pool:
            pool.starmap(annotate, task_args)


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
