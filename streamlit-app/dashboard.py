
# streamlit run [app name]

# Depuis une console :
# streamlit run dashboard.py

# Local URL: http://localhost:8501
# Network URL: http://192.168.0.89:8501

import streamlit as st
from PIL import Image
import json
import requests
from visualisation import plot_waterfall, plot_comparison

# Initial page config

global local
local = False

st.set_page_config(
    page_title='Prêt à dépenser',
    layout="wide",
    initial_sidebar_state="expanded",
)

# Appelle l'API distante en fournissant l'identifiant client (SK_ID_CURR)


def get_score(client_id):
    if (local == True):
        url = "http://127.0.0.1:8000/"
    else:
        url = "http://15.236.4.1/"

    response = requests.get(url + 'scoring/' + str(client_id))
    response = json.loads(response.text)
    return response

# Appelle l'API pour récupérer la liste des identifiants clients


def get_list_of_ids():
    if (local == True):
        url = "http://127.0.0.1:8000/"
    else:
        url = "http://15.236.4.1/"

    response = requests.get(url + 'list/')
    response = json.loads(response.text)
    result = dict(list_ids=response['all_ids'])
    return result['list_ids']

# Extrait de la réponse à get_score la décision, la probabilité, la liste des features les plus influentes
# et les valeurs shap de celles-ci


def extract_prediction(resp):
    result = dict(status=resp['status'], probability=resp['probability'], best_features=resp['best_features'],
                  shap_values=resp['shap_values'])
    return result

# Requête l'API distante pour obtenir les valeurs discrétisées d'une feature en particulier
# et la répartition des négatifs et positifs dans ces intervalles.
# L'objectif est de positionner le client.


def get_data_for_comparison(client_id, feature):
    if (local == True):
        url = "http://127.0.0.1:8000/"
    else:
        url = "http://15.236.4.1/"

    response = requests.get(
        url + 'client/' + str(client_id) + '/feature/' + feature)
    response = json.loads(response.text)
    return response


# Extrait de la réponse à la requête ci-dessus l'intervalle où le client se
# positionne pour une feature donnée, ainsi que les répartitions des targets sur les valeurs
# discrétisées de cette feature

def extract_comparison_data(resp):
    result = dict(original_value=resp['original_value'], interval=resp['interval'], target=resp['target'],
                  bins=resp['bins'], percent_of_target=resp['percent_of_target'])
    return result

# Ce panel permet de sélectionner l'identifiant d'un client, et d'afficher la réponse à la requête get_score


def panel_info_client(debug_mode):
    with st.container():
        col1, col2 = st.columns(2)
        status = -1
        best_features = []
        shap_values = []
        with col1:
            # Sélection de l'id du client
            st.selectbox("Sélectionner l'identifiant de votre client",
                         ['0'] + get_list_of_ids(), key='selected_id')
            client_id = '0' if st.session_state.selected_id == '0' else st.session_state.selected_id
            if debug_mode:
                st.write('You selected:', client_id)
        with col2:
            if int(client_id):
                # Afficher score et proba du score
                infos = get_score(client_id)
                resp = extract_prediction(infos)
                status = resp['status']
                proba = resp['probability']
                best_features = resp['best_features']
                shap_values = resp['shap_values']
                if (status == 1):
                    st.write('Risque de défaut de paiement avec une probabilité de ' +
                             str(round(100*float(proba), 2)) + ' %')
                if (status == 0):
                    st.write('Le prêt est accordé.')
                    st.write('La décision est fiable à ' +
                             str(round(100*float(proba), 2)) + ' %.')
                if (debug_mode):
                    # if debug afficher resp
                    with st.expander("### debug ###"):
                        st.write(resp)

    return client_id, status, best_features, shap_values

# Affichage des 15 features les plus influentes pour ce client,sous la forme d'un waterfall
# où les shap_values indiquent le sens de l'influence (vers 1 ou vers 0)


def show_decision_details(status, best_features, shap_values):
    with st.container():
        if (status != -1):
            fig = plot_waterfall(best_features, shap_values, status)
            st.plotly_chart(fig)

# Ce panel permet de sélectionner une feature et de récupérer la réponse
# de l'appel à get_data_for_comparison


def panel_positionnement(debug_mode, client_id, status, best_features):
    value = 0
    interval = 0
    target = []
    bins = []
    percent_of_target = []
    # Menu déroulant pour choisir les features en question
    # Ici on va positionner le client parmi des clients similaires pour les 15 features en question
    # (y compris le target à bien différencier)
    if (status != -1):
        with st.form('feature selection'):
            selected_feature = st.selectbox(
                label='Feature', options=best_features)
            submitted = st.form_submit_button('Submit')
            if submitted:
                resp = get_data_for_comparison(client_id, selected_feature)
                if (debug_mode):
                    # if debug afficher resp
                    with st.expander("### debug ###"):
                        st.write(resp)
                value = resp['original_value']
                interval = resp['interval']
                target = resp['target']
                bins = resp['bins']
                percent_of_target = resp['percent_of_target']

    return value, interval, target, bins, percent_of_target

# Affiche un graphique avec les répartitions des targets pour une feature donnée et la position du client


def show_comparison_details(value, interval, target, bins, percent_of_target):
    with st.container():
        if (target != []):
            fig = plot_comparison(value, interval, target,
                                  bins, percent_of_target)
            st.plotly_chart(fig)


def hc_sidebar():
    st.sidebar.header('Prêt à dépenser')
    image = Image.open('logo.jpg')
    st.sidebar.image(image)
    st.sidebar.markdown('Dashboard made by Sophie Piekarec')
    st.sidebar.markdown(
        '''Link to Streamlit doc :  https://docs.streamlit.io/''')


def hc_body():
    st.header('Evaluation des demandes de crédits')
    st.write('-----------------')
    debug_mode = st.checkbox('debug mode')
    client_id, status, best_features, shap_values = panel_info_client(
        debug_mode)
    tab1, tab2 = st.tabs(
        ["Explication de la décision", "Positionnement du client"])
    with tab1:
        show_decision_details(status, best_features, shap_values)
    with tab2:
        value, interval, target, bins, percent_of_target = panel_positionnement(
            debug_mode, client_id, status, best_features)
        if debug_mode :
            st.write(value)
        show_comparison_details(value, interval, target,
                                bins, percent_of_target)


def main():
    hc_sidebar()
    hc_body()


# Run main()

if __name__ == '__main__':
    main()
