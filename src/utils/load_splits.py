# Code for loading the training data that has been split.
import os
from os.path import join, exists
import glob
import pandas as pd
import pickle
from collections import defaultdict
import numpy as np
from src.utils import split_gen, sampling, configuration, paths
config = configuration.Config()

def get_ages_sample_paths(partition_type, phase, split, dataset):
    """
    Gets all of the sample paths for a given split.
    """
    
    # the asterisk works because this is just a template
    template = paths.get_sample_csv_path('eval', phase, split, dataset, partition_type, '*', config.n_across_time)
        
    all_age_sample_paths = glob.glob(template)
    
    age2path = {}
    for path in all_age_sample_paths:
        age = paths.extract_age_str(path)
        age2path[age] = path
    
    return age2path

    
def apply_if_subsample(data, path = None):
    """
    Applies subsampling logic for either development purposes or using a smaller sample than n = 500.
    Because the utterances were originally randomly sampled, taking a prefix of a random sample should also be a random sample.
    """
    
    assert config.n_beta == config.n_across_time, "Assumption for this code structure to hold."
    trunc_to_ideal = config.n_beta
    trunc_to =  min(trunc_to_ideal, data.shape[0])
    trunc_data = data.iloc[0:trunc_to]            
    return trunc_data    


def load_sample_model_across_time_args(split, dataset):
    
    sample_dict = defaultdict(dict)
    success_paths = get_ages_sample_paths('success', config.eval_phase, split, dataset)
    yyy_paths = get_ages_sample_paths('yyy', config.eval_phase, split, dataset)
    
    for name, path_set in zip(['success', 'yyy'], [success_paths, yyy_paths]):
        for age, path in path_set.items():
            this_data = pd.read_csv(path)
            this_data = apply_if_subsample(this_data)

            sample_dict[age][name] = this_data
        
    return sample_dict

def load_phono():
    
    return pd.read_pickle(join(config.prov_dir, 'pvd_all_tokens_phono_for_eval.pkl'))


def get_child_names():
    """
    Get all Providence children.
    """
    
    all_phono = load_phono()
    return sorted(list(set(all_phono.target_child_name)))

