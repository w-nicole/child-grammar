import copy
import pandas as pd
import os
import pickle
import numpy as np
from src.utils import configuration, likelihoods, load_models, transformers_bert_completions, load_splits
config = configuration.Config()


def sample_across_models(success_ids, yyy_ids, model, beta_values, lambda_values, examples_mode = False, all_tokens_phono=None):
    '''

        Efficiently compute posterior values computing to different parameterizations of the likelihood. Retrieve the priors once for a given model, compute the distances or WFST path lengths once, and then iterate over a range for the scaling parameter

        Args: 
        success_ids: utterance ids for utterances identified as communicative successes
        yyy_ids: utterance ids for utterances identified as communicative failures
        model: A model dictionary from the load models functions (not a HuggingFace model alone!)
        beta_values: a vector of scaling parameters to test for the Levenshtein distance
        lambda_values: a vector of scaling parameters to test for the WFST distance
        examples_mode: return extra information about the top 10 completions, appropriate for generating the example table in the paper, otherwise very memory intensive
        all_tokens_phono: for the examples table, moving the loading of phono up a level in the call stack avoids repeated data running

        Return
        A dataframe with all tokens scored for all models

    '''
     
    if all_tokens_phono is None:
        all_tokens_phono = load_splits.load_phono()
    this_bert_token_ids = all_tokens_phono.loc[all_tokens_phono.partition.isin(('success','yyy'))].bert_token_id
    initial_vocab, cmu_2syl_inchildes, cmu_indices_for_initial_vocab = load_models.get_initial_vocab_info()

    print('Running model '+model['title']+'...')

    # get the priors
    if model['type'] == 'BERT':
        priors_for_age_interval = transformers_bert_completions.compare_successes_failures(
            all_tokens_phono, success_ids, 
            yyy_ids, **model['kwargs'])

    elif model['type'] == 'unigram':
        priors_for_age_interval = transformers_bert_completions.compare_successes_failures_unigram_model(
            all_tokens_phono, success_ids, 
            yyy_ids, **model['kwargs'])
      
    score_store_single_model = []

    
    print('Computing WFST path lengths...')
    wfst_distances_for_age_interval_unreduced, ipa = likelihoods.get_wfst_distance_matrix(all_tokens_phono, priors_for_age_interval, initial_vocab,  cmu_2syl_inchildes, config.fst_path, config.fst_sym_path)    
    wfst_distances_for_age_interval_unreduced = -1 * np.log(wfst_distances_for_age_interval_unreduced + 10**-20) # convert this back to log space

    #for each word, find the citation pronunciation that is most likely to generate the observed data 
    wfst_distances_for_age_interval = likelihoods.reduce_duplicates(wfst_distances_for_age_interval_unreduced, cmu_2syl_inchildes, initial_vocab, 'min', cmu_indices_for_initial_vocab) # min for smallest surprisal

    for idx, lambda_value in enumerate(lambda_values):
        
        print(f'Processing lambda value {idx + 1} of {config.lambda_num_values}')

        # get the posteriors        
        if model['type'] == 'BERT':
            posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, 
                wfst_distances_for_age_interval, initial_vocab, None, lambda_value, examples_mode = examples_mode)

        elif model['type'] == 'unigram':
            posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, wfst_distances_for_age_interval, initial_vocab, this_bert_token_ids, lambda_value, examples_mode = examples_mode)
            print('If possible compare the bert_token_id in sample_across_models to the bert_token_id in one of the other scores sets from bert.')
            
        posteriors_for_age_interval['scores']['lambda_value'] = lambda_value
        posteriors_for_age_interval['scores']['model'] = model['title']
        posteriors_for_age_interval['scores']['likelihood_type'] = 'wfst'
        
        posteriors_for_age_interval['scores'].astype({'lambda_value' : 'float16'})
        this_score = copy.deepcopy(posteriors_for_age_interval['scores'])
        
        score_store_single_model.append(this_score)    


    print('Computing edit distances...')
    edit_distances_for_age_interval_unreduced = likelihoods.get_edit_distance_matrix(all_tokens_phono, priors_for_age_interval, cmu_2syl_inchildes)

    #for each word, find the citation pronunciation that is most likely to generate the observed data. Look for the one with the *smallest* edit distance     
    edit_distances_for_age_interval = likelihoods.reduce_duplicates(edit_distances_for_age_interval_unreduced, cmu_2syl_inchildes, initial_vocab, 'min', cmu_indices_for_initial_vocab)

    
    for idx, beta_value in enumerate(beta_values):
        
        print(f'Processing beta value {idx + 1} of {config.beta_num_values}')

        # get the posteriors        
        if model['type'] == 'BERT':
            posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, 
                edit_distances_for_age_interval, initial_vocab, None, beta_value, examples_mode = examples_mode)

        elif model['type'] == 'unigram':
            # special unigram hack
            
            posteriors_for_age_interval = transformers_bert_completions.get_posteriors(priors_for_age_interval, edit_distances_for_age_interval, 
                initial_vocab, this_bert_token_ids, beta_value, examples_mode = examples_mode)
            print('If possible compare the bert_token_id in sample_across_models to the bert_token_id in one of the other scores sets from bert.')
            
        posteriors_for_age_interval['scores']['beta_value'] = beta_value
        posteriors_for_age_interval['scores']['model'] = model['title']
        posteriors_for_age_interval['scores']['likelihood_type'] = 'levdist'
        
        posteriors_for_age_interval['scores'].astype({'beta_value' : 'float16'})
        this_score = copy.deepcopy(posteriors_for_age_interval['scores'])
        
        score_store_single_model.append(this_score)    

    all_scores = pd.concat(score_store_single_model)
    
    return all_scores 