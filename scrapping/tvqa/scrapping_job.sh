#!/bin/bash
#SBATCH --partition=batch
#SBATCH --job-name=scrapping_job%j
#SBATCH --output=scrapping_job%j.out
#SBATCH --error=scrapping_job%j.err
#SBATCH --mail-user=kirolos.ataallah@kaust.edu.sa
#SBATCH --mail-type=ALL
#SBATCH --time=0-30:30:00
#SBATCH --mem=32G
#SBATCH --nodes=1
## run the application:
/ibex/ai/home/ataallka/miniforge-pypy3/envs/gradio_test/bin/python3.9 -u scrapping_summaries.py