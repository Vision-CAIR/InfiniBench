import openai
import os
import argparse
import json
import ast
from multiprocessing.pool import Pool
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="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",
)


def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-3")
    parser.add_argument("--pred_path", required=True, help="/ibex/project/c2106/kirolos/MovieChat/workspace/benchmark_inference/benchmark_output_new/final/spoiler_questions.json")
    parser.add_argument("--output_dir", required=True, help="The path to save annotation json files.")
    parser.add_argument("--output_json", required=True, help="The path to save annotation final combined json file.")
    parser.add_argument("--api_key", required=True, help="OpenAI API key.")
    parser.add_argument("--num_tasks", required=True, type=int, help="Number of splits.")
    args = parser.parse_args()
    return args


def annotate(prediction_set, caption_files, output_dir):
    """
    Evaluates question and answer pairs using GPT-3
    Returns a score for correctness.
    """
    for file in caption_files:
        key = file[:-5] # Strip file extension
        qa_set = prediction_set[key]
        question = qa_set['q']
        answer = qa_set['a']
        pred = qa_set['pred']
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an intelligent chatbot designed to evaluate the correctness of generative outputs for multiple-choice questions (MCQs). "
                        "Your task is to compare the predicted answer with the correct answer and determine if the model chose the correct option. Here's how you can accomplish the task:\n"
                        "------\n"
                        "## INSTRUCTIONS:\n"
                        "- Focus on the meaningful match between the predicted answer and the correct answer.\n"
                        "- Consider synonyms or paraphrases as valid matches.\n"
                        "- Determine if the generated answer is correct or incorrect.\n"
                        "- Provide only 'yes' or 'no' to represent your evaluation decision.\n"
                        "- Evaluate as a human would, not as a machine.\n"
                        "- Provide your answer in the form of a Python dictionary string with the key 'decision', such as {'decision': 'yes'}.\n"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Please evaluate the following question-answer pair:\n\n"
                        f"Question: {question}\n"
                        f"Correct Answer: {answer}\n"
                        f"Predicted Answer: {pred}\n\n"
                        "Provide your evaluation as a decision where 'yes' means the model chose the correct option and 'no' means the model chose the wrong option.\n"
                        "Generate the response in the form of a Python dictionary string with the key 'decision'.\n"
                        "DO NOT PROVIDE ANY OTHER OUTPUT TEXT OR EXPLANATION. Only provide the Python dictionary string. "
                        "For example, your response should look like this: {'decision': 'yes'}.\n"
                        "Do not include any other information in your response such as ```python```."
                    )
                }
            ]
                
            )
            response_message = completion.choices[0].message.content
            response_message = response_message.replace("```", "")
            response_message = response_message.replace("python", "")
            response_message = response_message.replace("\n", "")
            try:
                response_dict = ast.literal_eval(response_message)
            except:
                response_dict=response_message
            result_qa_pair = [response_dict, qa_set]

            # Save the question-answer pairs to a json file.
            with open(f"{output_dir}/{key}.json", "w") as f:
                json.dump(result_qa_pair, f)

        except Exception as e:
            print(f"Error processing file '{key}': {e}")


def main():
    """
    Main function to control the flow of the program.
    """
    # Parse arguments.
    args = parse_args()

    file = open(args.pred_path)
    pred_contents = json.load(file)

    # Dictionary to store the count of occurrences for each video_id
    video_id_counts = {}
    new_pred_contents = []

    # Iterate through each sample in pred_contents
    for sample in pred_contents:
        video_id = sample['video_path_mp4'][1:].replace("/","_")
        if video_id in video_id_counts:
            video_id_counts[video_id] += 1
        else:
            video_id_counts[video_id] = 0

        # Create a new sample with the modified key
        new_sample = sample
        new_sample['video_path_mp4'] = f"{video_id}_{video_id_counts[video_id]}"
        new_pred_contents.append(new_sample)

    # Generating list of id's and corresponding files
    id_list = [x['video_path_mp4'] for x in new_pred_contents]
    caption_files = [f"{id}.json" for id in id_list]

    output_dir = args.output_dir
    # Generate output directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Preparing dictionary of question-answer sets
    prediction_set = {}
    for sample in new_pred_contents:
        id = sample['video_path_mp4']
        question = sample['Q']
        answer = sample['A']
        pred = sample['pred']
        qa_set = {"q": question, "a": answer, "pred": pred}
        prediction_set[id] = qa_set

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

            # Break the loop when there are no incomplete files
            if len(incomplete_files) == 0:
                break
            if len(incomplete_files) <= num_tasks:
                num_tasks = 1

            # Split tasks into parts.
            part_len = len(incomplete_files) // num_tasks
            all_parts = [incomplete_files[i:i + part_len] for i in range(0, len(incomplete_files), part_len)]
            task_args = [(prediction_set, part, args.output_dir) for part in all_parts]

            # Use a pool of workers to process the files in parallel.
            with Pool() as pool:
                pool.starmap(annotate, task_args)

        except Exception as e:
            print(f"Error: {e}")

    # Combine all the processed files into one
    combined_contents = {}
    json_path = args.output_json

    # Iterate through json files
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "r") as json_file:
                content = json.load(json_file)
                combined_contents[file_name[:-5]] = content

    # Write combined content to a json file
    with open(json_path, "w") as json_file:
        json.dump(combined_contents, json_file)
    print("All evaluation completed!")

    # Calculate accuracy
    yes_counter=0
    no_counter=0
    for key, result in combined_contents.items():
        # Computing score
        try :
            pred = result[0]['decision']
            if pred == 'yes':
                yes_counter+=1
            elif pred == 'no':
                no_counter+=1
        except:
            print("decision not found for", key)
            continue
    
    total = yes_counter + no_counter
    accuracy = yes_counter/total
    print("yes_counter:", yes_counter)
    print("no_counter:", no_counter)
    print("Accuracy:", accuracy)
    

if __name__ == "__main__":
    main()

