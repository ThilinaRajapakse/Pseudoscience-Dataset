import pandas as pd


df = pd.read_csv('data/snopes/data_all.tsv', sep='\t')

from pprint import pprint


pprint(df.head())