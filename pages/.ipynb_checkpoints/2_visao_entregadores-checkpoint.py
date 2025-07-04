import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="🚲" 
)

# =============================================
# FUNÇÕES
# =============================================
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe """
    linhas_selecionadas = (df1["Delivery_person_Age"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)
    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)
    df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format='%d-%m-%Y')
    linhas_selecionadas = (df1["multiple_deliveries"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1 = df1.loc[df1['City'] != 'NaN', :]
    df1 = df1.loc[df1['Weatherconditions'] != 'conditions NaN', :]
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.extract(r'(\d+)').astype(float)
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    return df1

# =============================================
# INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
# =============================================
# --- CORREÇÃO: Usando caminho relativo para o CSV ---
df_raw = load_data('train.csv')
df1 = clean_code(df_raw.copy())

st.header('Marketplace - Visão Entregadores')

# ==============================
# BARRA LATERAL
# ==============================
st.sidebar.markdown('### Cury company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""____""")

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="DD/MM/YYYY"
)
st.sidebar.markdown("""----""")

trafego_configuracoes = st.sidebar.multiselect(
    "Quais as condições do trânsito ?",
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'High', 'Medium', 'Jam']
)
st.sidebar.markdown("""----""")

# --- CORREÇÃO: Usando caminho relativo para a imagem ---
try:
    image = Image.open("foto eu.jpg")
    st.sidebar.markdown('### Feito por Gustavo Grecov')
    st.sidebar.image(image, width=150)
except FileNotFoundError:
    st.sidebar.error("Imagem 'foto eu.jpg' não encontrada.")


# Filtros
df1 = df1.loc[df1['Order_Date'] < date_slider, :]
df1 = df1.loc[df1['Road_traffic_density'].isin(trafego_configuracoes), :]

# ==============================
# LAYOUT CENTRAL
# ==============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.markdown('### Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_condição = df1['Vehicle_condition'].min()
            col3.metric('Melhor condição', melhor_condição)
        with col4:
            pior_condição = df1['Vehicle_condition'].max()
            col4.metric('Pior condição', pior_condição)
    
    with st.container():
        st.markdown("""-----""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings_per_deliver = df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            colsc = ['Delivery_person_Ratings', 'Road_traffic_density']
            dfe = df1.loc[:, colsc].groupby('Road_traffic_density').agg(['mean', 'std']).reset_index()
            dfe.columns = ['Trânsito', 'Média de Avaliação', 'Desvio Padrão']
            st.dataframe(dfe)
            
            st.markdown('##### Avaliação média por clima')
            dfc = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg(['mean', 'std']).reset_index()
            dfc.columns = ['Condições Climáticas', 'Média de Avaliação', 'Desvio Padrão']
            st.dataframe(dfc)

    with st.container():
        st.markdown("""-----""")
        st.title('Velocidade de Entregas')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df_fastest = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                           .groupby(['City', 'Delivery_person_ID'])
                           .min()
                           .sort_values(['City', 'Time_taken(min)'])
                           .reset_index())
            df_aux1 = df_fastest.loc[df_fastest['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df_fastest.loc[df_fastest['City'] == 'Urban', :].head(10)
            df_aux3 = df_fastest.loc[df_fastest['City'] == 'Semi-Urban', :].head(10)
            df_final = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            st.dataframe(df_final)
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_slowest = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                           .groupby(['City', 'Delivery_person_ID'])
                           .max()
                           .sort_values(['City', 'Time_taken(min)'], ascending=False)
                           .reset_index())
            df_aux1 = df_slowest.loc[df_slowest['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df_slowest.loc[df_slowest['City'] == 'Urban', :].head(10)
            df_aux3 = df_slowest.loc[df_slowest['City'] == 'Semi-Urban', :].head(10)
            df_final_slow = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            st.dataframe(df_final_slow)
