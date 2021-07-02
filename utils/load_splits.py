# Code for loading the training data that has been split.


import os
from os.path import join, exists
 
from utils import split_gen
import glob

import pandas as pd
import pickle

def sample_successes(task_name, split_name, dataset_name, data_dir, n = None, regenerate = False):
    """
    task_name = designates the cached value to use for optimizations.
        The cache should be different for beta optimization and run_models_across_time.
    """
    
    if n is None: # Assign the default values.
        assert task_name in ['beta', 'models_across_time'], "Invalid task name for sample successes -- use either 'beta' or 'models_across_time'."
        n = 5000 if task_name == 'beta' else 1000
        
    print('Note that this function will need to be changed for the eval data for the child optimizations -- rather than sample from the function, you should just probably use the val set.')
    
    this_data_folder = split_gen.get_split_folder(split_name, dataset_name, data_dir)
    success_utts = pd.read_csv(join(this_data_folder, 'success_utts.csv'))
    this_data_path = join(this_data_folder, f'success_utts_{task_name}_{n}.csv')
    
    if regenerate or not exists(this_data_path):
        # Need to sample the successes again and save them.
        success_utts_sample = success_utts.sample(n, replace=False).utterance_id
        success_utts_sample.to_csv(this_data_path)
    else:
        success_utts_sample = pd.read_csv(this_data_path)
    
    return success_utts_sample


##################
## TEXT LOADING ##
##################


def load_model_analysis_dict():
    
    """
    Try to load this model dictionary once at the beginning of the script, as it may take a while to initialize all of the models.
    """
    
    

def load_splits_folder_text(split, base_dir):
    
    folders = glob.glob(join(base_dir, split) +'/*') # List the child names
    
    data = {}
    for path in folders:
        name = path.split('/')[-1]
        data[name] = load_split_text_path(split, name, base_dir)
        
    return data


def load_split_text_path(split, dataset, base_dir):
    
    # What else is needed?
    
    train_text_path = join(split_gen.get_split_folder(split, dataset, base_dir), 'train.txt')
    val_text_path = join(split_gen.get_split_folder(split, dataset, base_dir), 'val.txt')
    
    # For the analyses? Think about what is required for yyy analysis.
    
    return {'train': train_text_path, 'val': val_text_path}
    
    
def load_eval_data_all(split_name, dataset_name, base_dir):
    
    """
    Loading cached data relevant to the model scoring functions in yyy analysis.
    """
    
    phono_filename = 'pvd_utt_glosses_phono_cleaned_inflated.pkl'
    success_utts_filename = 'success_utts.csv'
    yyy_utts_filename = 'yyy_utts.csv'

    data_filenames = [phono_filename, success_utts_filename, yyy_utts_filename]
    this_folder_path = split_gen.get_split_folder(split_name, dataset_name, base_dir)
    
    data_name = {
       'pvd_utt_glosses_phono_cleaned_inflated.pkl' : 'phono',
       'success_utts.csv' : 'success_utts',
       'yyy_utts.csv' : 'yyy_utts',
    }
    
    data_dict = {}
    for f in data_filenames:
        this_path = join(this_folder_path, f)
        data_dict[data_name[f]] = pd.read_csv(this_path) if f.endswith('.csv') else pd.read_pickle(this_path)
    
    return data_dict

def write_tagless_txt(orig_file_path):
    
    # You will need to remove "cgv" and "chi" from the text. How to do this?
    # you can remove it from the beginning and the end...
    # Is it OK just to string replace?
    
    # Remove the speaker tags
    clean_text = lambda text : text.strip('[CGV] ').strip('[CHI] ')
            
    # 6/17: https://stackoverflow.com/questions/10406135/unicodedecodeerror-ascii-codec-cant-decode-byte-0xd1-in-position-2-ordinal
    
    new_file_path = orig_file_path.split('.txt')[0] + '_no_tags.txt'
    
    all_clean_text = []
    with open(orig_file_path, 'r', encoding="utf-8") as f:
        for idx, line in enumerate(f.readlines()):
            all_clean_text.append(clean_text(line))
    
    with open(new_file_path, 'w') as nf:
        nf.writelines(all_clean_text)
    
    print(f'Wrote tagless train/val data to {new_file_path}.')

    return all_clean_text 
    
    
