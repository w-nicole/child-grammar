import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime


sys.path.append('.')
sys.path.append('src/.')
from src.utils import child_parser, child_models, utils_child, split_gen, load_models


if __name__ == '__main__':
    
    start_time = str(datetime.today())
    parser = child_parser.child_parser()
    
    # 7/7/21: https://stackoverflow.com/questions/17118999/python-argparse-unrecognized-arguments    
    raw_args = parser.parse_known_args()[0]
    # end cites
    # Not sure why known args is necessary here.
    
    this_model_args = vars(raw_args)
    data_child = this_model_args['data_child']
    prior_child = this_model_args['prior_child']
   
    this_model_dict = child_models.get_child_model_dict(prior_child)
    
    levdist_scores, beta_used = utils_child.score_cross_prior(data_child, prior_child, 'levdist')
    wfst_scores, lambda_used = utils_child.score_cross_prior(data_child, prior_child, 'wfst')
    scores =  pd.concat([levdist_scores, wfst_scores])
    
    score_path = utils_child.get_cross_path(data_child, prior_child)
    
    scores.to_pickle(score_path)
    
    print(f'Computations complete for: {data_child}, {prior_child}')
    print(f'Scores saved to: {score_path}')
    
    print(f'Started computations at: {start_time}')
    print(f'Finished computations at: {str(datetime.today())}')
   