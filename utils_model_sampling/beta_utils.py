
import os
from os.path import join, exists

import numpy as np

from utils import load_models, split_gen
import config

def get_beta_search_values():
    
    low = config.beta_low
    high = config.beta_high
    num_values = config.num_values
    
    if not config.grid_search:
        # Random hyperparam search
        beta_samples = np.random.uniform(low, high, num_values)
    else: # Grid search
        test_beta_vals = np.arange(low, high, (high - low) / num_values)
    
    return beta_samples


def load_beta_folder(split, dataset, is_tags, context_num):
    
    folder = split_gen.get_split_folder(split, dataset, config.eval_dir)
    this_title = load_models.query_model_title(split, dataset, is_tags, context_num)
    exp_path = join(folder, this_title.replace(' ', '_'))
    
    return join(folder, exp_path)

def load_beta_values(split_name, dataset_name, tags, context_width, eval_dir):
    
    exp_model_path = load_beta_folder(split_name, dataset_name, tags, context_width)
    results = pd.read_csv(join(exp_model_path, 'beta_search_results.csv'))
    # Below: temp line for checking the code interpretation.
    raw_results = pd.read_csv(join(exp_model_path, 'beta_search_raw_results.csv'))
    
    return results, raw_results

def get_optimal_beta_value(split, dataset, model_dict, eval_dir):
    
    # What to do here? Divide up loading the model name?
    
    this_beta_results, this_raw_beta_results = load_beta_values(split, dataset, model_dict['use_speaker_labels'], model_dict['context_width'])
    
    
    # Need to argmax for beta_value, given the posterior surprisal
    list_beta_results = list(this_beta_results['beta_value'])
    list_surp = list(this_beta_results['posterior_surprisal'])
    
    argmax_beta = np.argmax(list_surp)
    best_beta = list_beta_results[argmax_beta]
    
    print(f'All beta: {this_beta_results}')
    print(f'Chose beta: {best_beta}')
    
    return best_beta
    
    
    
    
    
