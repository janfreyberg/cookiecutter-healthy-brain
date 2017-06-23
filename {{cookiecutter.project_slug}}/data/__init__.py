from pathlib import Path
import pandas as pd


datafolder = Path('{{cookiecutter.local_data_folder}}')
# datafolder = Path('/Users/jan/Documents/eeg-data/cmi-hbn')

phenotypes = pd.read_csv('data/HBN_S1_Pheno_data.csv')
