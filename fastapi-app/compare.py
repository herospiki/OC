# Librairies

import pandas as pd
from pydantic import BaseModel

# 'feature', 'bin','TARGET','count', 'percent_of_target'

# Format de la réponse

class Clients(BaseModel):
    all_ids : list[int]

class Bins(BaseModel):
    interval: str
    target: list[int] = []
    bins: list[str] = []
    percent_of_target: list[float] = []


# Récupération des données clients dans le dataset


binned_data_df = pd.read_pickle('binned_data.pkl')
base_clients = pd.read_csv('sample_clients_for_demo.csv')

def get_list():
    list_ids = list(base_clients['SK_ID_CURR'].values)
    result = {'all_ids' : list_ids}
    return result

# Récupération de l'intervalle pour une valeur donnée à partir d'une liste d'intervalles

def get_interval(value, bin_list):
    size = len(bin_list)
    for i in range(0, size):
        if float(value) in bin_list[i]:
            return bin_list[i]

# Récupération pour une feature de la liste des bins et du bin pour une valeur donnée

def find_bins(binned_data_df, feature, value):
    cat_bins = binned_data_df[binned_data_df['feature']== feature]['bin'].unique()
    print(cat_bins)
    feature_bins = binned_data_df[binned_data_df['feature'] == feature]
    bin = get_interval(value, cat_bins)
    return bin, feature_bins


def get_features(client_id, feature):

    value = base_clients.loc[base_clients['SK_ID_CURR'] == client_id][feature]
    interval, feature_bins = find_bins(binned_data_df, feature, value)
    result = {'interval': str(interval),  
              'target': list(feature_bins['TARGET']), 
               'bins': list(feature_bins['bin'].astype('str')), 
               'percent_of_target': list(feature_bins['percent_of_target'])}
    return result
