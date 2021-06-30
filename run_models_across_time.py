
import os
from os.path import join, exists

from utils import load_models
from sample_models_across_time import successes_across_time_per_model

import pandas as pd

def load_sample_model_across_time_args(model_name):
    """
    How to load correct arguments for a given split?
    """
    
    utts_filename = None; all_tokens_phono_filename = None
    print('Update the load sample model across time args as new models are added.')
    
    this_utts_save_path = join('eval/new_splits', model_name)
    
    if ('meylan/meylan' in model_name) or ('all_old/all_old' in model_name):
        # From the original split, for replications.
        # I don't think these actually quite exist -- because the yyy needs to be regenerated, and the original sample was not saved.
        print('To cross-check this function with the original, you will need to load a cached value into the original yyy code -- and change that code.')
        utts_filename = pd.read_csv(join('all/all', )
        all_tokens_phono_filename = pd.read_csv()
    else if model_name == :
        utt_filename s
    
    utts = pd.read_csv(utts_filename)
    tokens_phono = pd.read_csv(all_tokens_phono_filename)
    
    if 'no_tags' in model_name:
        
    return utts, tokens_phono
        

if __name__ == '__main__':
    
    root_dir = '/home/nwong/chompsky/childes/child_listening_continuation/child-directed-listening'
    
    results_dir = 'intermediate_results/models_across_time'
    
    if not exists(results_dir):
        os.makedirs(results_dir)
        
    all_models = load_models.get_model_dict(root_dir)
    # Can you run this subprocess-style? What is best? For now just run sequentially because GPU.
    
    if this_model == 
    
    
    # Need to load from the right split -- how?
    utts_with_ages = 
    this_tokens_phono = 
    
    # Load the appropriate 
    ages = np.unique(utts_with_ages.year)
    
    for age in ages:
        for this_model in models:
            this_scores = successes_across_time_per_model(age, utts_with_ages, all_models[this_model], this_tokens_phono, root_dir)
            # Need to write the scores
            
    pass