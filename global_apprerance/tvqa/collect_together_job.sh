#!/bin/bash
#SBATCH --partition=batch
#SBATCH --job-name=collect_together%j
#SBATCH --output=collect_together%j.out
#SBATCH --error=collect_together%j.err
#SBATCH --mail-user=kirolos.ataallah@kaust.edu.sa
#SBATCH --mail-type=ALL
#SBATCH --time=0-40:30:00
#SBATCH --mem=100G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
## run the application:
/ibex/ai/home/ataallka/miniforge-pypy3/envs/long_video_bench/bin/python3.9 -u collect_together.py