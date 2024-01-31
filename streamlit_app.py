import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


st.title("Pré-traitement de l'export SELLSY")

from io import StringIO

uploaded_file = st.file_uploader("Importer un export SELLSY")
if uploaded_file is not None:
    # To read file as bytes:
    df_export_sellsy_init = pd.read_csv(uploaded_file,header = None)
    lst_factures_sans_ref_client = []

    for index in range(0,len(df_export_sellsy_init),2):
        if ";0000000000;" in df_export_sellsy_init.iloc[index, 0]:
            df_export_sellsy_temp = df_export_sellsy_init.drop([index,index + 1])
            lst_factures_sans_ref_client.append(index)
            lst_factures_sans_ref_client.append(index + 1)

    df_export_sellsy_sans_ref_client = df_export_sellsy_init.iloc[lst_factures_sans_ref_client]
    df_export_sellsy_sans_ref_client = df_export_sellsy_sans_ref_client.reset_index(drop=True)

    df_export_sellsy_temp = df_export_sellsy_temp.reset_index(drop=True)

    lst_factures_sans_da = []
    df_export_sellsy_new = df_export_sellsy_temp
    for index in range(1,len(df_export_sellsy_temp), 2):
        if ";0000000;" in df_export_sellsy_temp.iloc[index,0]:
            df_export_sellsy_new = df_export_sellsy_new.drop([index,index - 1])
            lst_factures_sans_da.append(index)
            lst_factures_sans_da.append(index - 1)

    df_export_sellsy_sans_da = df_export_sellsy_temp.iloc[lst_factures_sans_da]
    df_export_sellsy_sans_da = df_export_sellsy_sans_da.reset_index(drop=True)

    df_export_sellsy_new = df_export_sellsy_new.reset_index(drop=True)

    nb_factures_sans_da = int(len(df_export_sellsy_sans_da) / 2)
    nb_factures_sans_ref_client = int(len(df_export_sellsy_sans_ref_client) / 2)

    st.write("Nombre de factures sans ref client :", nb_factures_sans_ref_client)
    st.write("Nombre de factures sans DA :", nb_factures_sans_da)

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

