import os
from os.path import join, exists
import copy
import numpy as np
import pandas as pd
import glob
from collections import defaultdict
import pickle5 as pickle

from src.utils import load_models, transformers_bert_completions, load_splits, likelihoods, hyperparameter_utils, configuration, paths 
config = configuration.Config()

def successes_and_failures_across_time_per_model(age, success_ids, yyy_ids, model, all_tokens_phono, beta_value, likelihood_type):
    """
    model = a dict of a model like that in the yyy analysis 
    vocab is only invoked for unigram, which correspond to original yyy analysis.
    beta_value: generic name for beta (really a scaling value)
    
    Unlike original code assume that utts = the sample of utts_with_ages, not the whole dataframe
    """
    
    initial_vocab, cmu_in_initial_vocab, cmu_indices_for_initial_vocab  = load_models.get_initial_vocab_info()
    
    print('Running model '+model['title']+f'... at age {age}')
    
    # Note that if the age doesn't yield both successes and failures,
    # then one of the dataframes can be empty
    # causing runtime error -> program doesn't run to completion.
    # This is very unlikely for large samples, but potentially causes runtime errors in the middle of running.
    
    if model['model_type'] == 'BERT':
        priors_for_age_interval = transformers_bert_completions.compare_successes_failures(
            all_tokens_phono, success_ids, 
            yyy_ids, **model['kwargs'])

    elif model['model_type'] in ['data_unigram', 'flat_unigram']:
        priors_for_age_interval = transformers_bert_completions.compare_successes_failures_unigram_model(
            all_tokens_phono, success_ids, 
            yyy_ids, **model['kwargs'])
    else:
        raise ValueError('model_type not recognized!')
        
    if likelihood_type == 'levdist':
        likelihood_matrix = likelihoods.get_edit_distance_matrix(all_tokens_phono, 
            priors_for_age_interval, cmu_in_initial_vocab)            
    else:
        raise ValueError('Likelihood not recognized!')

    # likelihood_matrix has all pronunciation variants     
    likelihood_matrix = likelihoods.reduce_duplicates(likelihood_matrix, cmu_in_initial_vocab, initial_vocab, 'min', cmu_indices_for_initial_vocab)


    if model['model_type'] == 'BERT':
        posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, 
            likelihood_matrix, initial_vocab, scaling_value = beta_value, examples_mode = model['examples_mode'])
    elif model['model_type'] in ['data_unigram', 'flat_unigram']:
        # special unigram hack
        this_bert_token_ids = all_tokens_phono.loc[all_tokens_phono.partition.isin(('success','yyy'))].bert_token_id

        #this_bert_token_ids = unigram.get_sample_bert_token_ids()
        posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, likelihood_matrix, initial_vocab, this_bert_token_ids, scaling_value = beta_value, examples_mode = model['examples_mode'])
    else:
        raise ValueError('model_type not recognized!')

    posteriors_for_age_interval['scores']['age'] = age

    return copy.deepcopy(posteriors_for_age_interval['scores'])
   
