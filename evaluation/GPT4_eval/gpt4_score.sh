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

PRED="/ibex/project/c2106/kirolos/Long_video_Bench/evaluation/Goldfish_output/context_understanding.json"
OUTPUT_DIR="lwm_eval/score/deep_context_understanding"
# rm -rf $OUTPUT_DIR
NUM_TASKS=128
API_KEY="hhhh"



python GPT4_score.py \
    --pred_path ${PRED} \
    --output_dir "${OUTPUT_DIR}/fewshot_accuracy" \
    --output_json "${OUTPUT_DIR}/fewshot_accuracy_results.json"\
    --api_key $API_KEY \
    --num_tasks $NUM_TASKS

echo pred_path: $PRED