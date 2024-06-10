#!/bin/bash
#SBATCH --partition=batch
#SBATCH --mail-user=kirolos.ataallah@kaust.edu.sa
#SBATCH --mail-type=ALL
#SBATCH --job-name=frames_45_ckpt12%j
#SBATCH --output=frames_45_ckpt12%j.out
#SBATCH --error=frames_45_ckpt12%j.err
#SBATCH --time=0-10:00:00
#SBATCH --mem=64G
#SBATCH --nodes=1
## run the application:

# PRED="/ibex/project/c2106/kirolos/Long_video_Bench/evaluation/Goldfish_output/character_actions.json"
# OUTPUT_DIR="goldfish/mcq/character_actions"
# NUM_TASKS=128
# API_KEY="gpt4o_key"

PRED="path to the json prediction file"
OUTPUT_DIR="path to the output directory"
NUM_TASKS=128
API_KEY="gpt4o_key"



python GPT4_MCQ.py \
    --pred_path ${PRED} \
    --output_dir "${OUTPUT_DIR}/fewshot_accuracy" \
    --output_json "${OUTPUT_DIR}/fewshot_accuracy_results.json"\
    --api_key $API_KEY \
    --num_tasks $NUM_TASKS

echo pred_path: $PRED