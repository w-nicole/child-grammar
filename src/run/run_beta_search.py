import os
from os.path import join, exists
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from datetime import datetime
import sys

sys.path.append('.')
sys.path.append('src/.')
from src.utils import load_splits, load_models, split_gen, parsers, hyperparameter_utils, sample_across_models, child_models, configuration, paths
config = configuration.Config()

def optimize_beta_and_lambda(fitting_dict):
    '''
        Find the values of beta and lambda which minimize posterior surprisal; save this information in a place that run_models_across_time can load

        Args:
        split_name: If the model is a fine-tuned BERT model, is it trained on all CHILDES data, young children, or old chilren
        dataset_name: what dataset should be evaluated?
        model_dict: A model dictionary from the load models functions (not a HuggingFace model alone!)
        model_type: model label, choose 'childes' for fine-tuned BERT, 'adult' for off the shelf BERT, 'flat_unigram' for UniformPrior, 'data_unigram' for CHILDES-unigram
        
        Return: the best parameter values for WFST and Levenshtein distance likelihoods and accompanying scores. Plots these results as a side effect.

    '''

    beta_sample = hyperparameter_utils.get_hyperparameter_search_values('beta')
    lambda_sample = hyperparameter_utils.get_hyperparameter_search_values('lambda')
        
    # initial_vocab determines the softmax mask used by BERT, leave it as mask for all evaluations/training
    
    initial_vocab, cmu_in_initial_vocab, cmu_indices_for_initial_vocab  = load_models.get_initial_vocab_info()
    fitting_path =  paths.get_directory(fitting_dict)    
    
    if not exists(fitting_path):
        os.makedirs(fitting_path)
    
    success_utts_sample_path = paths.get_sample_csv_path(task_phase_to_sample_for='fit', split=fitting_dict['test_split'], dataset=fitting_dict['test_dataset'], data_type='success', age = None, n=config.n_beta)
    success_utts_sample  = pd.read_csv(success_utts_sample_path).utterance_id


    
    #success_utts_sample = load_splits.load_sample_successes(fitting_dict['test_split'], fitting_dict['test_dataset']).utterance_id
        
    # Don't use failures for beta search
    this_raw_beta_lambda_results = sample_across_models.sample_across_models(success_utts_sample, [], fitting_dict, beta_sample, lambda_sample)
    
    this_raw_beta_results = this_raw_beta_lambda_results.loc[this_raw_beta_lambda_results.likelihood_type == 'levdist']
    this_raw_lambda_results = this_raw_beta_lambda_results.loc[this_raw_beta_lambda_results.likelihood_type == 'wfst']

    # Log the beta results
    this_beta_results_surp = this_raw_beta_lambda_results.loc[this_raw_beta_lambda_results.likelihood_type == 'levdist'].groupby(['beta_value']).posterior_probability.agg(lambda x: np.mean(-1 * np.log(x))).reset_index()
    this_beta_results_surp = this_beta_results_surp.rename(columns = {'posterior_probability' : 'posterior_surprisal'})
    beta_results_path = join(fitting_path, f'beta_search_results_{config.n_beta}.csv')
    this_beta_results_surp.to_csv(beta_results_path)
    print("Writing beta results to", {beta_results_path})
    #plot_hyperparameter_optimization(fitting_path, 'beta', beta_sample, this_beta_results_surp['posterior_surprisal'], split_name, dataset_name)
    
    
    # Log the lamba results
    this_lambda_results_surp = this_raw_beta_lambda_results.loc[this_raw_beta_lambda_results.likelihood_type == 'wfst'].groupby(['lambda_value']).posterior_probability.agg(lambda x: np.mean(-1 * np.log(x))
).reset_index()
    this_lambda_results_surp = this_lambda_results_surp.rename(columns = {'posterior_probability' : 'posterior_surprisal'})
    lambda_results_path = join(fitting_path, f'lambda_search_results_{config.n_beta}.csv')
    this_lambda_results_surp.to_csv(lambda_results_path)
    print("Writing lambda results to", {lambda_results_path})
    #plot_hyperparameter_optimization(fitting_path, 'lambda', lambda_sample, this_lambda_results_surp['posterior_surprisal'], split_name, dataset_name)
    


    return this_raw_beta_results, this_beta_results_surp, this_raw_lambda_results, this_lambda_results_surp
    
def plot_hyperparameter_optimization(fig_path_dir, hyperparameter_name, hyperparameters, hyperparameter_surprisals, split, dataset):

    print('Deprecated')
    #this increases the failure surface to have this run as part of a large job

    '''
    Generate figures to look at scores across each hyperparamter range

    Args:
    fig_path_dir: directory to output to
    hyperparameter_name: 'beta' or 'lambda'
    hyperparameters: values of the hyperparameters (x axis)
    hyperparameter_surprisals: scores associated with each hyperparameter
    split: which subset of samples should be used to compute the scores
    dataset: which dataset should this be scored against 

    Return:
    Path to the figure saved to disk

    '''
    
    plt.title(hyperparameter_name +f' optimization for Split: {split}, Dataset: {dataset}')
    plt.xlabel(hyperparameter_name+' value')
    plt.ylabel('Posterior surprisal')
    plt.scatter(hyperparameters, hyperparameter_surprisals)
    
    fig_path = join(fig_path_dir, hyperparameter_name+f'_optimization_{config.n_beta}.png')
    plt.savefig(fname = fig_path)
    plt.close()
    print(f'Writing optimization plot to: {fig_path}')
    return fig_path
    
if __name__ == '__main__':    
    
    start_time = str(datetime.today())
    parser = parsers.split_parser()
    
    # 7/7/21: https://stackoverflow.com/questions/17118999/python-argparse-unrecognized-arguments    
    raw_args = parser.parse_known_args()[0]    
    this_model_args = vars(raw_args)

    # If training_dataset or training_split is defined, use its value to determine the model to load. Otherwise assume that `dataset` and `split` are overloaded and that the value should be used in order to choose both the dataet to test against and the model to load


    this_model_args['task_phase'] = 'fit'
    this_model_args['n_samples'] = config.n_across_time   
    print(this_model_args)             
    
    this_model_dict = load_models.get_fitted_model_dict(this_model_args)

    print('Loaded the model!')    
    raw_beta_results, beta_results, raw_lambda_results, lambda_results = optimize_beta_and_lambda(this_model_dict)

    print(f'Computations complete for model:')
    print(this_model_dict)
    print(f'Started computations at: {start_time}')
    print(f'Finished computations at: {str(datetime.today())}')