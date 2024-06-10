import openai
import os
import argparse
import warnings
import json
import ast
from multiprocessing.pool import Pool

warnings.filterwarnings('ignore')
from openai import OpenAI

def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-4")
    parser.add_argument("--summaries_folder", default='path to the folder containing the episodes summaries')
    parser.add_argument("--scripts_folder", default='path to the folder containing episodes Screenplay Scripts')
    parser.add_argument("--output_dir", default='path to the folder where the output json files will be saved')
    parser.add_argument("--output_json", default="path to the output json file where all the qa pairs will be saved")
    parser.add_argument("--api_key",required=True)
    parser.add_argument("--num_tasks", default=128, type=int)
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
    for file in caption_files:
        key = file[:-5] # Strip file extension.
        caption = gt_file[key]
        script=gt_script[key]
        try:
            # Generate GPT-4o response.
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": 
                            "You play two roles: a human asking questions related to a video and an intelligent chatbot designed to help people find information from a given video. "
                            "------"
                            "##TASK: "
                            "Your task is to first play the role of a human who asks questions related to deep context understanding in the video and then play the role of an AI assistant that provides information based on the video content."
                            "Users will provide human video summary and the video script,and you will generate a conversation-like question and answers pair specifically focusing on measuring the viewer's context understanding. "
                            "------"
                            "##INSTRUCTIONS:"
                            "- The questions must be conversational, as if a human is asking them, and should directly relate to deep context understanding for the video content. "
                            "- The answers must be detailed, descriptive, and should directly reference the information provided."
                            "- The number of questions should be up to 20 questions and answers."
                            "- The questions should be tricky and hard to answer to measure the viewer's context understanding."
                            "- The answers must be detailed, descriptive, and should directly reference the information provided."
                            "- It will be good if most of the questions are related to the visual content of the video."
                            "-Again the questions should be very tricky and hard to answer to measure the viewer's context understanding." 
                            "Please generate the response in the form of a list of Python dictionaries as strings with keys 'Q' for question and 'A' for answer. Each corresponding value should be the question and answer text respectively. "
                            "For example, your response should look like this: [{'Q': 'Your question here...', 'A': 'Your answer here...'},{'Q': 'Your question here...', 'A': 'Your answer here...'}]."
                            "please only output the required format, do not include any additional information."
                            "If you want to type 's or 't and so on please use \u2019s for 's and \u2019t for 't and so on."
                            "Test your output by using the python ast library to parse your output list."
                            "Remember well the output format of ONLY a PYTHON LIST as output\n"
                    },
                    {
                        "role": "user",
                        "content":
                            f"video summary: {caption}. "
                            f"video transcript: {script}. \n"
                            "Please generate up to 20 questions and treir answers in the form of list of Python dictionaries string with keys 'Q' for question and 'A' for answer. Each corresponding value should be the question and answer text respectively. "
                            "For example, your response should look like this: [{'Q': 'Your question here...', 'A': 'Your answer here...'},{'Q': 'Your question here...', 'A': 'Your answer here...'}]. "
                    }
                ]
            )
            # Convert response to a Python dictionary.
            print("requested")
            response_message = completion.choices[0].message.content
            response_message=response_message.replace("’","'")
            response_message = response_message.replace("'s", "\u2019s")  
            response_message = response_message.replace("s'", "s\u2019")   
            response_message = response_message.replace("'t", "\u2019t")    
            response_message = response_message.replace("```", "")
            response_message = response_message.replace("```python", "")
            
            try:          
                response_dict = ast.literal_eval(response_message)
            except:
                completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role":"user",
                        "content":
                            f"Given this response message: {response_message}\n"
                            "Fix this response to be a valid python list that can be parsed by ast.literal_eval() function\n"
                            "output only the python list without any other information"
                            "Output list should be like this example: [{'Q': 'question here...', 'A': 'answer here...'},{'Q': 'question here...', 'A': 'answer here...'},...]"
                    }

                ]
                )
                # Convert response to a Python dictionary.
                response_message = completion.choices[0].message.content
                print("requested again")
                try :
                    response_dict = ast.literal_eval(response_message)
                    # Save the question-answer pairs to a json file.
                    with open(f"{output_dir}/{key}.json", "w") as f:
                        json.dump(response_dict, f)
                except:
                    print("Error parsing response message second time: ")
                    response_dict = response_message
                    # Save the question-answer pairs to a json file.
                    os.makedirs(f"{output_dir}_mm", exist_ok=True)
                    with open(f"{output_dir}_mm/{key}.json", "w") as f:
                        json.dump(response_dict, f)
        except Exception as e:
            print(f"Error processing file '{key}': {e}")


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
    # while True:
    #     try:
    # Files that have not been processed yet.
    completed_files = os.listdir(output_dir)
    print(f"completed_files: {len(completed_files)}")

    # Files that have not been processed yet.
    incomplete_files = [f for f in caption_files if f not in completed_files]
    print(f"incomplete_files: {len(incomplete_files)}")

    # if len(incomplete_files) == 0:
    #     break
    if len(incomplete_files) <= num_tasks:
        num_tasks = 1

    # Split tasks into parts.
    part_len = len(incomplete_files) // num_tasks
    all_parts = [incomplete_files[i:i + part_len] for i in range(0, len(incomplete_files), part_len)]
    task_args = [(gt_captions,gt_scripts, part, args.output_dir) for part in all_parts]

    # Use a pool of workers to process the files in parallel.
    with Pool() as pool:
        pool.starmap(annotate, task_args)

        # except Exception as e:
        #     print(f"Error: {e}")

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
