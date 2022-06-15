import os
import sys
from os.path import join, exists
import copy

sys.path.append('.')
sys.path.append('src/.')
from src.utils import paths, configuration, scripts
config = configuration.Config()  


def gen_fitting_commands(fitting_spec_dict):
    
    paths.validate_spec_dict(fitting_spec_dict, config.spec_dict_params)
    paths.validate_phase(fitting_spec_dict['task_phase'], config.task_phases)
    
    
    mem_alloc_gb, time_alloc_hrs,  n_tasks, cpus_per_task = scripts.get_training_alloc(fitting_spec_dict['training_dataset'])

    header_commands = scripts.gen_command_header(mem_alloc_gb = mem_alloc_gb, time_alloc_hrs = time_alloc_hrs,
        n_tasks = n_tasks,
        cpus_per_task = cpus_per_task,        
        two_gpus = False)
    slurm_commands = header_commands

    fitting_output_path = paths.get_directory(fitting_spec_dict)    
    if not exists(fitting_output_path):
        os.makedirs(fitting_output_path)    

    slurm_commands += [f"rm -rf {fitting_output_path}\n"]  # clear the directory in case it had stuff in it before
    slurm_commands += [f"mkdir -p {fitting_output_path}\n"]  # make the training directory if necessary     
    slurm_commands += ["mkdir ~/.cache/$SLURM_JOB_ID\n"]


    model_input_spec_dict = copy.copy(fitting_spec_dict)
    model_input_spec_dict['task_phase'] = 'train'
    model_input_spec_dict['context_width'] = None
    model_input_spec_dict['test_split'] = None
    model_input_spec_dict['test_dataset'] = None
    model_input_dir = paths.get_directory(model_input_spec_dict)

    sh_loc = 'output/SLURM/'+fitting_spec_dict['task_name']+'_'+fitting_spec_dict['task_phase']
    
    if not exists(sh_loc):
        os.makedirs(sh_loc)
    
    sing_header = scripts.gen_singularity_header()   
    # slurm_commands += [f"{sing_header} {gen_eval_scripts.get_one_python_command('src/run/run_beta_search.py', fitting_spec_dict['test_split'], fitting_spec_dict['test_dataset'] , fitting_spec_dict['use_tags'], fitting_spec_dict['context_width'], fitting_spec_dict['model_type'], fitting_spec_dict['training_dataset'], fitting_spec_dict['training_split'])[1]}\n"]    

    slurm_commands += [f"{sing_header} {scripts.get_python_run_command('src/run/run_beta_search.py', fitting_spec_dict)}\n"]

        
    slurm_filename = os.path.join(sh_loc, paths.get_slurm_script_name(fitting_spec_dict))


    return slurm_filename, slurm_commands