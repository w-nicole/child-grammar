#!/bin/bash

#SBATCH -N 1
#SBATCH -p cpl
#SBATCH -t 00:10:00
#SBATCH --mem=1G
#SBATCH --output=/om2/user/wongn/child-directed-listening/%j_gen-scripts_2a.out 

module load openmind/singularity/3.2.0

# scripts for nonchild, scripts for shelf models, scripts for finetune models

<<<<<<< HEAD:scripts_run_tiers/tier_2a_non_child_train_shelf_scores.sh
singularity exec --nv -B /om,/om2/user/wongn /om2/user/wongn/vagrant/trans-pytorch-gpu python3 gen_training_scripts.py & singularity exec --nv -B /om,/om2/user/wongn /om2/user/wongn/vagrant/trans-pytorch-gpu python3 gen_sample_scripts.py;

chmod u+x /home/wongn/child_repo_split/submit_non_child_train.sh;
chmod u+x /home/wongn/child_repo_split/submit_non_child_beta_time_shelf.sh;
=======
singularity exec --nv -B /om,/om2/user/wongn /om2/user/wongn/vagrant/trans-pytorch-gpu python3 gen_training_scripts.py & singularity exec --nv -B /om,/om2/user/wongn /om2/user/wongn/vagrant/trans-pytorch-gpu python3 gen_sample_scripts.py; chmod u+x submit_non_child_train.sh & chmod u+x submit_non_child_beta_time_shelf.sh;
>>>>>>> origin/scriptless_master:tier_2a_non_child_train_shelf_scores.sh

# train non-child models + score shelf models 

/home/wongn/child_repo_split/submit_non_child_beta_time_shelf.sh & /home/wongn/child_repo_split/submit_non_child_train.sh

# If in development: At this point, rsync models/scores to Chompsky