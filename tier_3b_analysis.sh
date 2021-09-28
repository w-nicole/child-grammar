
rm 'Examples for Succcess and Failure Table.nbconvert.ipynb'
rm 'Models across time analyses.nbconvert.ipynb'
rm 'Child evaluations.nbconvert.ipynb'
rm 'Prevalence analyses.nbconvert.ipynb'

jupyter nbconvert --execute 'Examples for Success and Failure Table.ipynb' --to notebook
jupyter nbconvert --execute 'Models across time analyses.ipynb' --to notebook
jupyter nbconvert --execute 'Child evaluations.ipynb' --to notebook
jupyter nbconvert --execute 'Prevalence analyses.ipynb' --to notebook

