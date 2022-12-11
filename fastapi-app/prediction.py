# Librairies

import pandas as pd
import pickle
from pydantic import BaseModel
import re

# Format de la réponse 

class Prediction(BaseModel):
    status : int # 0 ou 1
    probability : float
    best_features : list[str] = []
    shap_values : list[float] = []


# Récupération des données clients dans le dataset 

data = pd.read_csv('sample_clients_for_demo.csv')

data = data.drop(columns=['TARGET'])

#data = data.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))

# Chargement du modèle final 

with open("final_model.sav", "rb") as f:
    loaded_model = pickle.load(f)

# Récupérer les meilleures features et les shap_values

def get_best_features(n_feat, model, customer, features):
    length = len(customer.columns) 
  
    # renvoit la classe '0' ou'1' (proba 0.5)

    pred_value = int(model.predict(customer)[0])

    # renvoit la probabilité d'appartenir à la classe déterminée
    pred_proba = model.predict_proba(customer)[0][pred_value]

    # renvoit les shap values de  features
    shap_values= model.predict(customer,pred_contrib=True)
 
    shap_df = pd.DataFrame(shap_values[0][0:length]).T
 
    shap_df.columns= features
    abs_shap_values = abs(shap_df.T)
    # extraction de la liste des best features et des valeurs correspondantes
    best_features = abs_shap_values.nlargest(n_feat,0).index.values
    values = shap_df[best_features].values[0]
    #best_features = []
    #values = []

    return pred_value, pred_proba, best_features, values


# renvoit la classe '0' ou'1'
# renvoit la probabilité d'appartenir à la classe '1'


def predict(client_id):

    customer = data[data['SK_ID_CURR'] == client_id].drop(columns=['SK_ID_CURR'])
    features = list(data.drop(columns = ['SK_ID_CURR']).columns.values)
  
    pred_value, pred_proba, best_features, values = get_best_features(15, loaded_model, customer, features)
    pred_result = {"status": pred_value, "probability": pred_proba, 'best_features': list(best_features), 
    'shap_values' : list(values)}
    return pred_result
