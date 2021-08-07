#!/bin/bash

# For the command text
# 6/24/21: https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Singularity-container%3F
# and https://github.mit.edu/MGHPCC/OpenMind/issues/3392
# including the bash line at the top, and all but the python3 commands

#SBATCH -N 1
#SBATCH -p cpl
#SBATCH --gres=gpu:2
#SBATCH -t 9:00:00
#SBATCH --mem=9G
#SBATCH --constraint=high-capacity
#SBATCH --output=/om2/user/wongn/child-directed-listening/experiments/scripts_train_lr_0.001_epochs_5/models/all/all/%j_training_tags=True.out
mkdir -p /om2/user/wongn/child-directed-listening/experiments/scripts_train_lr_0.001_epochs_5/models/all/all

module load openmind/singularity/3.2.0
mkdir ~/.cache/$SLURM_JOB_ID
# 7/13/21: https://stackoverflow.com/questions/19960332/use-slurm-job-id for variable name of job ID
singularity exec --nv -B /om,/om2/user/wongn /om2/user/wongn/vagrant/trans-pytorch-gpu     python3 run_mlm_lr_0.001_max_epochs_5.py             --model_name_or_path bert-base-uncased             --do_train             --do_eval             --output_dir /om2/user/wongn/child-directed-listening/experiments/scripts_train_lr_0.0001_epochs_5/models/all/all/with_tags            --train_file /om2/user/wongn/child-directed-listening/finetune/all/all/train.txt             --validation_file /om2/user/wongn/child-directed-listening/finetune/all/all/val.txt             --cache_dir ~/.cache/$SLURM_JOB_ID	--overwrite_output_dir

# end taken command code 6/24/21 and slurm id reference 7/13/21