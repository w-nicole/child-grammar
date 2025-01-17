import os
from os.path import join, exists
import pandas as pd
import numpy as np
from src.utils import data_cleaning, configuration, paths
config = configuration.Config()

# 7/23/21: https://www.mikulskibartosz.name/how-to-set-the-global-random_state-in-scikit-learn/
# Information reference, not for code -- sufficient to seed numpy for sklearn.

SEED = config.SEED
np.random.seed(SEED)

import sklearn
from sklearn import model_selection

def get_age_split_data(raw_data, months = config.age_split):
    
    data = raw_data.dropna(subset = ['target_child_age'])
    
    young_mask = data['target_child_age'] <= months * 30.5
    old_mask = data['target_child_age'] > months * 30.5
    
    young_df = data[young_mask]
    old_df = data[old_mask]

    return young_df, old_df



def save_all_chi_vocab(train_data):
    
    """
    Note: This only accepts the all/all split.
            It expects cleaned "utt_glosses" (data) with all errors removed.
    Note: If you load train_data from a saved df, it will convert list -> str which will mess up the token identification.
    'token' should be re-cast to list for correct behavior, as seen below.
    """
    
    chi_data = train_data.loc[train_data.speaker_code == 'CHI']
    
    tokens = [y for x in chi_data['tokens'] for y in x]
    
    token_frequencies = pd.Series(tokens).value_counts().reset_index()
    token_frequencies.columns = ['word','count']
    
    save_path = paths.get_chi_vocab_path()
    token_frequencies.to_csv(save_path)
    print(f'CHI vocabulary frequencies saved to: {save_path}')
    
    # Do not use things marked chi_vocab, they are from the past version.
   
    return token_frequencies

    

def determine_split_idxs(unsorted_cleaned_data, split_on, val_ratio = None, val_num = None):
    """
    Split off a subset of a pool of data to be used as validation.
    This function was changed from the original.
    
    If you want to use a model with context, transformers_bert_completions requires transcript id to be the splitting attr
        for disjointedness guarantees.
    If you want to use a child model,
        split on utterance id, and set context argument = None, to never use context (otherwise the eval diversity is too small).
    """
    
    assert (val_ratio is not None) ^ (val_num is not None), 'Exactly one of val_ratio and val_num should be specified.'
    
    data = unsorted_cleaned_data.copy()
    
    data = data.sort_values(by=[split_on])
    
    split_attr_inventory = np.unique(data[split_on])
    
    # Note: always put at least one transcript in val, because other train data will be joined to train
    # for child finetuning data
    
    sample_num = val_num if val_ratio is None else max(1, int(float(val_ratio) * len(split_attr_inventory)))
    
    train_idx, validation_idx = sklearn.model_selection.train_test_split(split_attr_inventory, test_size = sample_num)
    
    return train_idx, validation_idx 


def filter_text_from_content(lines):
    
    remove_tags = lambda this_str : this_str.replace('[CHI] ', ''). replace('[CGV] ', '')
    return list(map(remove_tags, lines))

def filter_text(text_path):
    """
    8/14/21: Just refactored this into two layers after initial text generation
        to support the subsampling in gen_partial_dataset.
    """
    with open(text_path, 'r') as f:
        all_str = filter_text_from_content(f.readlines())
        
    return all_str

    
def write_partition(phase, phase_data, split_folder):

    if not exists(split_folder):
        os.makedirs(split_folder)
    
    this_file_path = join(split_folder, f'{phase}.txt')

    phase_data[['gloss_with_punct']].to_csv(this_file_path, index=False, header=False)
     
    print(f'File written to {this_file_path}')


def assign_and_find_phase_data(phase, split_on, phase_idxs, data_pool, phase_label='phase'):
    """
    Different from the original function, re-test
    See dtermine_split_idxs comments on what to split on for which models.
        basically child = utterance_id, anything else = transcript_id.
    """
    
    data_pool.loc[data_pool[split_on].isin(phase_idxs), phase_label] = phase
    
    phase_data = data_pool.loc[data_pool[phase_label] == phase]
    
    return phase_data, data_pool
    
    
def write_data_partitions_text(all_data, split_folder, phase, phase_idxs, split_on, phase_label='phase'):
    """
    See determine_split_idxs comments on what to use for split_on argument per split type.
    Need to test this function, it has changed.
    """
 
    # this_phase_data, all_data_with_assignments = assign_and_find_phase_data(phase, split_on, phase_idxs, all_data, phase_label)
    

   #all_data.loc[all_data[split_on].isin(phase_idxs),
   #          'phase'] = phase
    
    this_phase_data, all_data_with_assignments = assign_and_find_phase_data(phase, split_on, phase_idxs, all_data, phase_label)
   
    # This is needed in case you write from all_tokens_phono,
    # Because you never want to write errors (at the utterance level) into the finetune text file.
    
    phase_data_clean = data_cleaning.drop_errors(this_phase_data) 
    
    # Need to make this_phase_data have unique utterance ids
    # Otherwise, you will write repetitively to the source.
    # This is important for Pvd data
    
    phase_data_by_utts = phase_data_clean[['utterance_id', 'gloss_with_punct']].drop_duplicates()
    
    # Make sure that each id is paired with one gloss with punct.
    # i.e. no single id has two different glosses with punct.
    
    assert len(set(phase_data_clean['utterance_id'])) == phase_data_by_utts.shape[0]    

    write_partition(phase, phase_data_by_utts, split_folder)
    
    return all_data, this_phase_data


def exec_split_gen(cleaned_utt_glosses, split_output_folder, phase, split_on = 'transcript_id'):
    
    train_idxs, val_idxs = determine_split_idxs(cleaned_utt_glosses, split_on, val_ratio = config.val_ratio)

    split_glosses_df, train_df = write_data_partitions_text(cleaned_utt_glosses, split_output_folder, 'train', train_idxs, split_on)
    
    split_glosses_df, _ = write_data_partitions_text(split_glosses_df, split_output_folder, 'eval', val_idxs, split_on)


    glosses_path = join(split_output_folder, 'data_pool_with_phases.pkl')
    split_glosses_df.to_pickle(glosses_path)
    
    print(f'Writing split glosses to: {glosses_path}')
    return split_glosses_df, train_df


