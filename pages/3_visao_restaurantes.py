import pandas as pd
from haversine import haversine
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Visão Restaurantes",
    page_icon="🍽️"
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

@st.cache_data
def distance(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = np.round(df1['distance'].mean(), 2)
    return avg_distance

@st.cache_data
def avg_time_with_festival(df1):
    df_aux = df1.loc[df1['Festival'] == 'Yes', :]
    if not df_aux.empty:
        df_agg = df_aux.loc[:, ['Time_taken(min)']].agg({'Time_taken(min)': ['mean', 'std']})
        tempo_festival = np.round(df_agg.iloc[0, 0], 2)
        std_festival = np.round(df_agg.iloc[1, 0], 2)
        return tempo_festival, std_festival
    return 0, 0

@st.cache_data
def avg_time_without_festival(df1):
    df_aux = df1.loc[df1['Festival'] == 'No', :]
    if not df_aux.empty:
        df_agg = df_aux.loc[:, ['Time_taken(min)']].agg({'Time_taken(min)': ['mean', 'std']})
        tempo_sem_festival = np.round(df_agg.iloc[0, 0], 2)
        std_sem_festival = np.round(df_agg.iloc[1, 0], 2)
        return tempo_sem_festival, std_sem_festival
    return 0, 0

# =============================================
# INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
# =============================================
# --- CORREÇÃO: Usando caminho relativo para o CSV ---
df_raw = load_data('train.csv')
df1 = clean_code(df_raw.copy())

st.header('Marketplace - Visão Restaurantes')

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
        st.title("Overal Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1['Delivery_person_ID'].unique())
            st.metric('Entregadores', delivery_unique)
        with col2:
            avg_distance_val = distance(df1)
            st.metric('Distância Média', avg_distance_val)
        with col3:
            tempo_festival, _ = avg_time_with_festival(df1)
            st.metric('Tempo Médio C/ Festival', tempo_festival)
        with col4:
            _, std_festival = avg_time_with_festival(df1)
            st.metric('Desvio Padrão C/ Festival', std_festival)
        with col5:
            tempo_sem_festival, _ = avg_time_without_festival(df1)
            st.metric('Tempo Médio S/ Festival', tempo_sem_festival)
        with col6:
            _, std_sem_festival = avg_time_without_festival(df1)
            st.metric('Desvio Padrão S/ Festival', std_sem_festival)

    with st.container():
        st.markdown("""-----""")
        st.title("Tempo Médio de Entrega por Cidade")
        df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""-----""")
        st.title("Distribuição do Tempo")
        col1, col2 = st.columns(2)
        with col1:
            avg_distance_df = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance_df['City'], values=avg_distance_df['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""-----""")
        st.title("Distribuição da Distância")
        df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)