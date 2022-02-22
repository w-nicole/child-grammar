import os
from os.path import join, exists
import json
from datetime import datetime
import sys

sys.path.append('.')
sys.path.append('src/.')
from src.utils import scripts, split_gen, child_models, configuration
config = configuration.Config()
from src.gen import gen_sample_scripts


def models_get_split_folder(split_type, dataset_type, with_tags):
    
    tags_str = 'with_tags' if with_tags else 'no_tags' # For naming the model folder
    
    base_dir = f'output/experiments/{config.exp_determiner}/models'
    return join(base_dir, join(join(split_type, dataset_type), tags_str))


def get_training_alloc(split_name):
        
    time, mem, n_tasks, cpus_per_task = gen_sample_scripts.time_and_mem_alloc()
    if split_name != 'child':
        time = 24 if not config.dev_mode else (0, 30, 0)                
    
    return mem, time, n_tasks, cpus_per_task
    
    
def get_training_header_commands(split_name, dataset_name, with_tags, om2_user = config.slurm_user, lr = None):
    
    time_alloc_hrs, mem_alloc_gb, n_tasks, cpus_per_task = get_training_alloc(split_name)
    
    model_dir = models_get_split_folder(split_name, dataset_name, with_tags)
    
    print('Use of cvt root dir will not be compatible with eventual updating datetime in gen_training_scripts')
    
    header_commands = scripts.gen_command_header(mem_alloc_gb = mem_alloc_gb, time_alloc_hrs = time_alloc_hrs,
                                        n_tasks = n_tasks, cpus_per_task = cpus_per_task,
                                          slurm_folder = scripts.get_slurm_folder(split_name, dataset_name, task = 'non_child_train'),
                                          slurm_name = f'training_tags={with_tags}{f"_{lr}" if lr is not None else ""}', 
                                          two_gpus = (dataset_name in {'young', 'all'}))
    return header_commands
    
    
def get_isolated_training_commands(split_name, dataset_name, with_tags, om2_user = config.slurm_user):
    
    header_commands = get_training_header_commands(split_name, dataset_name, with_tags, om2_user)
    non_header_commands = get_non_header_commands(split_name, dataset_name, with_tags, om2_user)
    
    commands = header_commands + non_header_commands
    
    return commands


def get_run_mlm_command(split_name, dataset_name, this_data_dir, this_model_dir, tags_data_str, om2_user):
    
    this_args_dict = config.child_args if split_name == 'child' else config.general_training_args
    
    if split_name == 'child':
        _, is_tags = child_models.get_best_child_base_model_path()
        base_model = models_get_split_folder('all', 'all', is_tags)
    else:
        base_model = 'bert-base-uncased'
        
    this_args_dict['model_name_or_path'] = base_model
    
    this_args_list = sorted(list(this_args_dict.keys())) # readability
    
    data_args = [
            f"--train_file {this_data_dir}/train{tags_data_str}.txt",
            f"--validation_file {this_data_dir}/val{tags_data_str}.txt", 
            f"--cache_dir ~/.cache/$SLURM_JOB_ID",
            f"--output_dir {this_model_dir}",
        ]
    
    trainer_args = [
        f"--{key} {this_args_dict[key]}"
        for key in this_args_list
    ]
    
    if config.dev_mode:
        trainer_args += [
            f"--max_train_samples 10",
            f"--max_eval_samples 10",
        ]

    main_command = f"singularity exec --nv -B /om,/om2/user/{om2_user} /om2/user/{om2_user}/vagrant/ubuntu20.simg"
    this_python_command = f' python3 src/run/run_mlm.py {" ".join(data_args + trainer_args)}'

    return f"{main_command}{this_python_command}"
    

def get_non_header_commands(split_name, dataset_name, with_tags, om2_user = config.slurm_user):
    
    tags_data_str  = '' if with_tags else '_no_tags' # For loading the proper data
    
    model_dir = models_get_split_folder(split_name, dataset_name, with_tags)
    
    data_dir = join(config.finetune_dir, join(split_name, dataset_name))
        
    commands = []
   
    # For the command text
    # 6/24/21: https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Singularity-container%3F
    # and https://github.mit.edu/MGHPCC/OpenMind/issues/3392
    # including the bash line at the top

    # 7/13/21: https://stackoverflow.com/questions/19960332/use-slurm-job-id
    # Got the variable guidance for what variable name to use for job id
    commands.append("mkdir ~/.cache/$SLURM_JOB_ID\n")
    # end usage of variable
    commands.append("# 7/13/21: https://stackoverflow.com/questions/19960332/use-slurm-job-id for variable name of job ID\n")
    
    main_command_all = get_run_mlm_command(split_name, dataset_name, data_dir, model_dir, tags_data_str, om2_user)
    
    commands.append(main_command_all)
    
    # end 7/13/21
    # end taken command code 6/24/21

    commands.append("\n# end taken command code 6/24/21 and slurm id reference 7/13/21")
    return commands


if __name__ == '__main__':
    
    label = 'non_child_train'
    
    all_splits = [('all', 'all'), ('age', 'old'), ('age', 'young'), ('switchboard','all')]
    
    for split_args in all_splits:

        # childes datasets should be run with and without tags
        if split_args[0] in ('all','age'):
            for has_tags in [True, False]:
                t_split, t_dataset = split_args
                tags_str = 'with_tags' if has_tags else 'no_tags'
                output_directory = os.path.join(config.project_root, f'output/SLURM/scripts_{label}/{tags_str}') 
                scripts.write_training_shell_script(t_split, t_dataset, has_tags, output_directory, get_isolated_training_commands)

        # other datasets, eg switchboard should be run without tags only
        else: 
            has_tags = False
            t_split, t_dataset = split_args
            tags_str = 'no_tags'
            output_directory = os.path.join(config.project_root, f'output/SLURM/scripts_{label}/{tags_str}') 
            scripts.write_training_shell_script(t_split, t_dataset, has_tags, output_directory, get_isolated_training_commands)

    scripts.gen_submit_script(label, config.childes_model_args, label)