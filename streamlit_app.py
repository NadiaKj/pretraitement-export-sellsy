import altair as alt
import numpy as np
import pandas as pd
import re
import streamlit as st


st.title("Pré-traitement de l'export SELLSY")

from io import StringIO

uploaded_file_app = st.file_uploader("Importer un export SELLSY")

if uploaded_file_app is not None :
    # Chargement données:
    df_export_sellsy_init = pd.read_csv(uploaded_file_app,sep='\t',header = None)

    # Retrait des ",":
    df_export_sellsy_init = df_export_sellsy_init.replace(',','',regex=True)

    #Extraction des factures/avoirs sans ref_client
    lst_factures_sans_ref_client = []
    df_export_sellsy_temp = df_export_sellsy_init
    for index in range(0,len(df_export_sellsy_init),2):
        if ";0000000000;" in df_export_sellsy_init.iloc[index, 0]:
            df_export_sellsy_temp = df_export_sellsy_temp.drop([index,index + 1])
            lst_factures_sans_ref_client.append(index)
            lst_factures_sans_ref_client.append(index + 1)

    df_export_sellsy_sans_ref_client = df_export_sellsy_init.iloc[lst_factures_sans_ref_client]
    df_export_sellsy_sans_ref_client = df_export_sellsy_sans_ref_client.reset_index(drop=True)

    df_export_sellsy_temp = df_export_sellsy_temp.reset_index(drop=True)
    
    #Extraction des factures/avoirs sans da
    lst_factures_sans_da = []
    df_export_sellsy_new = df_export_sellsy_temp
    
    for index in range(1,len(df_export_sellsy_temp), 2):
        if ";0000000;" in df_export_sellsy_temp.iloc[index,0]:
            df_export_sellsy_new = df_export_sellsy_new.drop([index,index - 1])
            lst_factures_sans_da.append(index - 1)
            lst_factures_sans_da.append(index)
        
    df_export_sellsy_sans_da = df_export_sellsy_temp.iloc[lst_factures_sans_da]
    df_export_sellsy_sans_da = df_export_sellsy_sans_da.reset_index(drop=True)

    # Extraction des données OK
    df_export_sellsy_new = df_export_sellsy_new.reset_index(drop=True)

    # Résumé de l'import
    nb_lignes_total = int(len(df_export_sellsy_init) / 2)
    nb_lignes_factures = len(df_export_sellsy_init[df_export_sellsy_init[0].str.contains(";F-")])
    nb_lignes_avoirs = len(df_export_sellsy_init[df_export_sellsy_init[0].str.contains(";AVR-")])
    nb_factures_sans_da = int(len(df_export_sellsy_sans_da) / 2)
    nb_factures_sans_ref_client = int(len(df_export_sellsy_sans_ref_client) / 2)

    st.write("Nombre de lignes totales :", nb_lignes_total)
    st.write("Nombre de factures :", nb_lignes_factures)
    st.write("Nombre d'avoirs :", nb_lignes_avoirs)

    st.write("Nombre de factures/avoirs sans ref client :", nb_factures_sans_ref_client)
    st.write("Nombre de factures/avoirs sans DA :", nb_factures_sans_da)

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(header = False, index = False).encode('utf-8')

    csv_ok = convert_df(df_export_sellsy_new)
    csv_ko_ref_client = convert_df(df_export_sellsy_sans_ref_client)
    csv_ko_da = convert_df(df_export_sellsy_sans_da)

    st.download_button(
        label="Fichier OK (à importer dans SICOMPTA)",
        data=csv_ok,
        file_name='export_sellsy_ok.csv',
        mime='text/csv',
    )

    st.download_button(
            label="Fichier avec factures sans ref client",
            data=csv_ko_ref_client,
            file_name='export_sellsy_factures_sans_ref_client.csv',
            mime='text/csv',
        )
    
    st.download_button(
            label="Fichier avec factures sans DA",
            data=csv_ko_da,
            file_name='export_sellsyfactures_sans_da.csv',
            mime='text/csv',
        )
    
    st.header("Comparaison avec les données SELLSY")
    uploaded_file_factures_sellsy = st.file_uploader("Importer la liste des factures SELLSY", help="La liste des factures doit être téléchargée à partir de Sellsy, avec le filtre 'Date du document' utilisant les mêmes dates que l'export Sellsy, et inclure obligatoirement la colonne 'Numéro'")
    uploaded_file_avoirs_sellsy = st.file_uploader("Importer la liste des avoirs SELLSY", help="La liste des avoirs doit être téléchargée à partir de Sellsy, avec le filtre 'Date du document' utilisant les mêmes dates que l'export Sellsy, et inclure obligatoirement la colonne 'Numéro'")

if uploaded_file_app is not None and uploaded_file_factures_sellsy is not None and uploaded_file_avoirs_sellsy is not None :
    df_factures_sellsy = pd.read_csv(uploaded_file_factures_sellsy,sep=';', encoding="ISO-8859-1")
    df_avoirs_sellsy = pd.read_csv(uploaded_file_avoirs_sellsy,sep=';', encoding="ISO-8859-1")
    lst_factures_export = []
    lst_avoirs_export = []

        # Définition d'une fonction pour extraire le numéro des factures
    def trouver_facture(chaine):
        # Utilisation de l'expression régulière pour trouver le motif F- suivi de chiffres
        motif = re.search(r'F-\d+-\d+', chaine)
        # Si un motif est trouvé, retournez-le, sinon retournez None
        if motif:
            return motif.group()
        else:
            return None

    # Définition d'une fonction pour extraire le numéro des avoirs
    def trouver_avoir(chaine):
        # Utilisation de l'expression régulière pour trouver le motif AVR- suivi de chiffres
        motif = re.search(r'AVR-\d+-\d+', chaine)
        # Si un motif est trouvé, retournez-le, sinon retournez None
        if motif:
            return motif.group()
        else:
            return None

    # Application de la fonction pour extraire la liste des factures de l'export Sellsy    
    for index in range(0,len(df_export_sellsy_init),2):
        num_facture = trouver_facture(df_export_sellsy_init.iloc[index, 0])
        if num_facture is not None:
            lst_factures_export.append(num_facture)

    # Application de la fonction pour extraire la liste des avoirs de l'export Sellsy    
    for index in range(0,len(df_export_sellsy_init),2):
        num_avoir = trouver_avoir(df_export_sellsy_init.iloc[index, 0])
        if num_avoir is not None:
            lst_avoirs_export.append(num_avoir)

    # Liste des factures Sellsy
    lst_factures_sellsy = df_factures_sellsy["Numéro"].to_list()

    # Liste des avoirs Sellsy
    lst_avoirs_sellsy = df_avoirs_sellsy["Numéro"].to_list()

    # Comparaison factures Sellsy et export
    factures_manquantes = [x for x in lst_factures_sellsy if x not in lst_factures_export]

    # Comparaison factures Sellsy et export
    avoirs_manquants = [x for x in lst_avoirs_sellsy if x not in lst_avoirs_export]


    ##st.write("Liste factures :", lst_factures_export)
    ##st.write("Liste avoirs :", lst_avoirs_export)

    st.write("Factures manquantes :",factures_manquantes)
    st.write("Avoirs manquants :",avoirs_manquants)