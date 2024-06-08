#!/bin/bash
#SBATCH --partition=batch
#SBATCH --job-name=scrapping_bbt%j
#SBATCH --output=scrapping_bbt%j.out
#SBATCH --error=scrapping_bbt%j.err
#SBATCH --mail-user=kirolos.ataallah@kaust.edu.sa
#SBATCH --mail-type=ALL
#SBATCH --time=0-30:30:00
#SBATCH --mem=32G
#SBATCH --nodes=1
## run the application:
/ibex/ai/home/ataallka/miniforge-pypy3/envs/gradio_test/bin/python3.9 -u bbt_scrapping.py