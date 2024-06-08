#!/bin/bash
#SBATCH --partition=batch
#SBATCH --job-name=castle_scrappring%j
#SBATCH --output=castle_scrappring%j.out
#SBATCH --error=castle_scrappring%j.err
#SBATCH --mail-user=kirolos.ataallah@kaust.edu.sa
#SBATCH --mail-type=ALL
#SBATCH --time=0-30:30:00
#SBATCH --mem=32G
#SBATCH --nodes=1
## run the application:
/ibex/ai/home/ataallka/miniforge-pypy3/envs/long_video_bench/bin/python3.9 -u castle_scrappring.py