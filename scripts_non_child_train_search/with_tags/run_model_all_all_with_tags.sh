#!/bin/bash

# For the command text
# 6/24/21: https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Singularity-container%3F
# and https://github.mit.edu/MGHPCC/OpenMind/issues/3392
# including the bash line at the top, and all but the python3 commands

#SBATCH -N 1
#SBATCH -p cpl
#SBATCH --gres=gpu:2
#SBATCH -t 1:30:00
#SBATCH --mem=9G
#SBATCH --constraint=high-capacity
#SBATCH --output=/om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all/%j_training_tags=True.out
mkdir -p /om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all

module load openmind/singularity/3.2.0
mkdir ~/.cache/$SLURM_JOB_ID
# 7/13/21: https://stackoverflow.com/questions/19960332/use-slurm-job-id for variable name of job ID
singularity exec --nv -B /om,/om2/user/wongn /om2/user/wongn/vagrant/trans-pytorch-gpu python3 run_mlm.py --train_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/train.txt --validation_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/val.txt --cache_dir ~/.cache/$SLURM_JOB_ID --output_dir /om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all/with_tags/0.001 --learning_rate=0.001 --do_eval  --do_train  --eval_steps 100 --evaluation_strategy steps --load_best_model_at_end  --logging_steps 100 --logging_strategy steps --metric_for_best_model eval_loss --model_name_or_path bert-base-uncased --num_train_epochs 5 --overwrite_output_dir  --per_device_eval_batch_size 8 --per_device_train_batch_size 8 --save_steps 100 --save_strategy steps --save_total_limit 1 --weight_decay 1e-07;  python3 run_mlm.py --train_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/train.txt --validation_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/val.txt --cache_dir ~/.cache/$SLURM_JOB_ID --output_dir /om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all/with_tags/0.00075 --learning_rate=0.00075 --do_eval  --do_train  --eval_steps 100 --evaluation_strategy steps --load_best_model_at_end  --logging_steps 100 --logging_strategy steps --metric_for_best_model eval_loss --model_name_or_path bert-base-uncased --num_train_epochs 5 --overwrite_output_dir  --per_device_eval_batch_size 8 --per_device_train_batch_size 8 --save_steps 100 --save_strategy steps --save_total_limit 1 --weight_decay 1e-07;  python3 run_mlm.py --train_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/train.txt --validation_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/val.txt --cache_dir ~/.cache/$SLURM_JOB_ID --output_dir /om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all/with_tags/0.0005 --learning_rate=0.0005 --do_eval  --do_train  --eval_steps 100 --evaluation_strategy steps --load_best_model_at_end  --logging_steps 100 --logging_strategy steps --metric_for_best_model eval_loss --model_name_or_path bert-base-uncased --num_train_epochs 5 --overwrite_output_dir  --per_device_eval_batch_size 8 --per_device_train_batch_size 8 --save_steps 100 --save_strategy steps --save_total_limit 1 --weight_decay 1e-07;  python3 run_mlm.py --train_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/train.txt --validation_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/val.txt --cache_dir ~/.cache/$SLURM_JOB_ID --output_dir /om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all/with_tags/0.0001 --learning_rate=0.0001 --do_eval  --do_train  --eval_steps 100 --evaluation_strategy steps --load_best_model_at_end  --logging_steps 100 --logging_strategy steps --metric_for_best_model eval_loss --model_name_or_path bert-base-uncased --num_train_epochs 5 --overwrite_output_dir  --per_device_eval_batch_size 8 --per_device_train_batch_size 8 --save_steps 100 --save_strategy steps --save_total_limit 1 --weight_decay 1e-07;  python3 run_mlm.py --train_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/train.txt --validation_file /om2/user/wongn/child-directed-listening/finetune_cut_46000/all/all/val.txt --cache_dir ~/.cache/$SLURM_JOB_ID --output_dir /om2/user/wongn/child-directed-listening/experiments/lr_search/models/all/all/with_tags/5e-05 --learning_rate=5e-05 --do_eval  --do_train  --eval_steps 100 --evaluation_strategy steps --load_best_model_at_end  --logging_steps 100 --logging_strategy steps --metric_for_best_model eval_loss --model_name_or_path bert-base-uncased --num_train_epochs 5 --overwrite_output_dir  --per_device_eval_batch_size 8 --per_device_train_batch_size 8 --save_steps 100 --save_strategy steps --save_total_limit 1 --weight_decay 1e-07
# end taken command code 6/24/21 and slurm id reference 7/13/21