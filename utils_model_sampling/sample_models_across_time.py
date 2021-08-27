
import os
from os.path import join, exists

import copy
from utils import load_models, transformers_bert_completions, unigram, load_splits
from utils_model_sampling import beta_utils

from collections import defaultdict
import numpy as np

import pandas as pd

import glob


def assemble_scores_no_order():
    """
    Assumes order of the the model vs age loop doesn't matter.
    """
    
    # is_subset is for development purposes
    
    this_load_args = load_models.gen_all_model_args()
    
    score_store = []
    
    for split, dataset, tags, context, model_type in this_load_args:

       
        this_beta_folder = beta_utils.load_beta_folder(split, dataset, tags, context, model_type)

        age_paths = glob.glob(join(this_beta_folder, 'run_models_across_time_*.pkl'))
        
        for this_data_path in age_paths:
            
            data_df = pd.read_pickle(this_data_path)
            
            ## TEMPORARY ONLY -- REMOVE THIS SECTION ###

            print('REMOVE THIS TEMPORARY SECTION IN SAMPLE_MODELS_ACROSS_TIME, only used for loading temp scores n = 2')
            if 'posterior_surprisal' in data_df.columns:
                data_df = data_df.rename(columns={'posterior_surprisal' : 'posterior_probability',
                                                'prior_surprisal' : 'prior_probability'})
            
            ## END TEMPORARY -- NEED TO REMOVE THIS SECTION BEFORE n = 500 ###
            
            score_store.append(data_df)
                      
    return score_store



def successes_and_failures_across_time_per_model(age, success_ids, yyy_ids, model, all_tokens_phono, beta_value, examples_mode):
    """
    model = a dict of a model like that in the yyy analysis 
    vocab is only invoked for unigram, which correspond to original yyy analysis.
    
    Unlike original code assume that utts = the sample of utts_with_ages, not the whole dataframe
    """
    
    initial_vocab, cmu_in_initial_vocab = load_models.get_initial_vocab_info()
    
    print('Running model '+model['title']+f'... at age {age}')
    
    # Note that if the age doesn't yield both successes and failures,
    # then one of the dataframes can be empty
    # causing runtime error -> program doesn't run to completion.
    # This is very unlikely for large samples, but potentially causes runtime errors in the middle of running.
    
    if model['type'] == 'BERT':
        priors_for_age_interval = transformers_bert_completions.compare_successes_failures(
            all_tokens_phono, success_ids, 
            yyy_ids, **model['kwargs'])

    elif model['type'] == 'unigram':
        priors_for_age_interval = transformers_bert_completions.compare_successes_failures_unigram_model(
            all_tokens_phono, success_ids, 
            yyy_ids, **model['kwargs'])

    edit_distances_for_age_interval = transformers_bert_completions.get_edit_distance_matrix(all_tokens_phono, 
        priors_for_age_interval, initial_vocab, cmu_in_initial_vocab)            

    if model['type'] == 'BERT':
        posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, 
            edit_distances_for_age_interval, initial_vocab, beta_value = beta_value, examples_mode = examples_mode)
    elif model['type'] == 'unigram':
        # special unigram hack
        this_bert_token_ids = unigram.get_sample_bert_token_ids()
        posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, edit_distances_for_age_interval, initial_vocab, this_bert_token_ids, beta_value = beta_value, examples_mode = examples_mode)


    posteriors_for_age_interval['scores']['model'] = model['title']
    posteriors_for_age_interval['scores']['age'] = age
    
    return copy.deepcopy(posteriors_for_age_interval['scores'])
   