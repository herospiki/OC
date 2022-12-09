
# streamlit run [app name]

# Depuis une console : 
#streamlit run https://github/ /dashboard.py

#Local URL: http://localhost:8501
#Network URL: http://192.168.0.89:8501

import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import json
import requests
from visualisation import plot_waterfall, plot_comparison

# Initial page config

global local
local = True



st.set_page_config(
     page_title='Prêt à dépenser',
     layout="wide",
     initial_sidebar_state="expanded",
)

#@st.cache
#def load_data(path):
#    data = pd.read_pickle(path)
#    return data

#data = load_data('../backend/sample_clients.pkl')

# request the prediction API with the client_id number (SK_ID_CURR)

def get_score(client_id): 
    if (local == True) :
        url = "http://127.0.0.1:8000/"
    else:
        url= "http://15.236.4.1/"

    response = requests.get(url + 'scoring/' + str(client_id)) 
    response = json.loads(response.text)
    return response

def get_list_of_ids(): 
    if (local == True) :
        url = "http://127.0.0.1:8000/"
    else:
        url= "http://15.236.4.1/"

    response = requests.get(url + 'list/' ) 
    response = json.loads(response.text)
    result = dict(list_ids=response['all_ids'])
    return result['list_ids']

def extract_prediction(resp):
	result = dict(status=resp['status'],probability=resp['probability'], best_features=resp['best_features'],
    shap_values = resp['shap_values'])
	return result 


def get_data_for_comparison(client_id, feature): 
    if (local == True) :
        url = "http://127.0.0.1:8000/"
    else:
        url= "http://15.236.4.1/"

    response = requests.get(url + 'client/' + str(client_id) + '/feature/' + feature) 
    response = json.loads(response.text)
    return response

def extract_comparison_data(resp):
	result = dict(interval=resp['interval'],target=resp['target'], bins=resp['bins'],
    percent_of_target= resp['percent_of_target'])
	return result 


def enter_id_client():
    client_id = st.text_input('Label', 'Enter client id',label_visibility='hidden',key="placeholder")
    return client_id

  
def panel_info_client(debug_mode):
    with st.container():
        col1, col2 = st.columns(2)
        status = -1
        best_features = []
        shap_values = []
        with col1:
           # tab1, tab2 = st.tabs(["Saisie directe", "Recherche"])
            #with tab1:
            #    st.write('Enter client id')
            #    client_id = st.text_input('Label', st.session_state.selected_id,label_visibility='hidden',key="placeholder")
            #with tab2:
            st.selectbox("Sélectionner l'identifiant de votre client",
                ['0'] + get_list_of_ids(), key='selected_id')
            client_id = '0' if st.session_state.selected_id == '0' else st.session_state.selected_id
            if debug_mode :
                st.write('You selected:', client_id)
          #with st.expander("Liste des identifiants clients"):
          #        st.write(get_list_of_ids())
            #if int(client_id) :
               # Préparer les fonctions avec les infos qu'on veut afficher
               # base client
             #   st.markdown('Infos client')
        
        with col2:
            if int(client_id) :
                #st.markdown('Décision')
            # Afficher score et proba du score  
                infos = get_score(client_id)
                resp = extract_prediction(infos)
                status = resp['status']
                proba = resp['probability']
                #threshold = resp['threshold']
                best_features = resp['best_features']
                shap_values = resp['shap_values']
                if (status == 1): 
                    st.write('Risque de défaut de paiement avec une probabilité de '+ 
                    str(round(100*float(proba), 2)) + ' %')
                if (status == 0):
                    st.write('Le prêt est accordé.')
                    st.write('La décision est fiable à '+ str(round(100*float(proba), 2)) + ' %.')
                if (debug_mode) :
            # if debug afficher resp
                    with st.expander("### debug ###"):
                        st.write(resp)
    
    return client_id, status, best_features, shap_values

def show_decision_details(status, best_features, shap_values):
    with st.container():
        if (status != -1) :
            fig = plot_waterfall(best_features, shap_values, status)
            st.plotly_chart(fig)


def panel_positionnement(debug_mode,client_id, status, best_features):
    interval = 0
    target=[]
    bins=[]
    percent_of_target=[]
    # Menu déroulant pour choisir les features en question
    # Ici on va positionner le client parmi des clients similaires pour les 15 features en question (y compris le target
    # à bien différencier)
    if (status != -1) :
        with st.form('feature selection'):
                selected_feature = st.selectbox(label = 'Feature', options = best_features)
                submitted = st.form_submit_button('Submit') 
                if submitted :
                    resp = get_data_for_comparison(client_id, selected_feature)
                    if (debug_mode) :
                        # if debug afficher resp
                          with st.expander("### debug ###"):
                            st.write(resp)
                    interval = resp['interval']
                    target = resp['target']
                    bins = resp['bins']
                    percent_of_target = resp['percent_of_target']
                  
    return interval, target, bins, percent_of_target
            
def show_comparison_details(interval, target, bins, percent_of_target):
    with st.container():
        if (target != []) :
            fig = plot_comparison(interval, target, bins, percent_of_target)
            st.plotly_chart(fig)

def hc_sidebar():
    st.sidebar.header('Prêt à dépenser')
    image = Image.open('logo.jpg')
    st.sidebar.image(image)
    #st.sidebar.subheader('ABOUT')
    st.sidebar.markdown('Dashboard made by Sophie Piekarec')
    st.sidebar.markdown('''Link to Streamlit doc :  https://docs.streamlit.io/''')

def hc_body():  
    st.header('Evaluation des demandes de crédits')
    st.write('-----------------')
    debug_mode = st.checkbox('debug mode')
    client_id, status, best_features, shap_values = panel_info_client(debug_mode)
    tab1, tab2 = st.tabs(["Explication de la décision", "Positionnement du client"])
    with tab1:
          show_decision_details(status, best_features, shap_values)
    with tab2:
        interval, target, bins, percent_of_target = panel_positionnement(debug_mode,client_id, status, best_features)
        show_comparison_details(interval, target, bins, percent_of_target)

def main():
    hc_sidebar()
    hc_body()
   

# Run main()

if __name__ == '__main__':
    main()