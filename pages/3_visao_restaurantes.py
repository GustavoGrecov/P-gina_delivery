import pandas as pd
from haversine import haversine
import plotly.express as px
import streamlit as st 
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import numpy as np
from haversine import haversine
import plotly.graph_objects as go 
from datetime import datetime
st.set_page_config(
    page_title="Visão Restaurantes",
    page_icon="🍽️" 
)

df = pd.read_csv("C:/Users/greco/Trabalho/portifolio/train.csv")
#limpando o dataset
df1 = df.copy()
linhas_selecionadas = (df1["Delivery_person_Age"] != "NaN ")
df1 = df1.loc[linhas_selecionadas, :].copy()
df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype( int )
df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype( float)
df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format='%d-%m-%Y')
linhas_selecionadas = (df1["multiple_deliveries"] != "NaN ")
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
#limpando os espaços nas linhas
df1.loc[: , 'ID'] = df1.loc[: , 'ID'].str.strip()
df1.loc[: , 'Delivery_person_ID'] = df1.loc[: , 'Delivery_person_ID'].str.strip()
df1.loc[: , 'Road_traffic_density'] = df1.loc[: , 'Road_traffic_density'].str.strip()
df1.loc[: , 'Type_of_order'] = df1.loc[: , 'Type_of_order'].str.strip()
df1.loc[: , 'Type_of_vehicle'] = df1.loc[: , 'Type_of_vehicle'].str.strip()
df1.loc[: , 'Festival'] = df1.loc[: , 'Festival'].str.strip()
df1.loc[: , 'City'] = df1.loc[: , 'City'].str.strip()
df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
df1 =  df1.loc[df1['City'] != 'NaN' , :]
df1 = df1.loc[df1['Weatherconditions'] != 'conditions NaN' , :]
df1 = df1.loc[df1['Road_traffic_density'] !=  'NaN' , :]
def calcular_distancia(row):
    ponto_restaurante = (row['Restaurant_latitude'], row['Restaurant_longitude'])
    ponto_entrega = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
    return geodesic(ponto_restaurante, ponto_entrega).kilometers
df1['Distancia'] = df1.apply(calcular_distancia, axis=1 )
# Remover "(min)" e espaços extras, depois converter para número
df1['Time_taken(min)'] = df1['Time_taken(min)'].str.extract(r'(\d+)').astype(float)

# Visão Empresa
st.header('Marketplace - Visão Restaurantes')

#====================================================
# BARRA LATERAL 
#====================================================
st.sidebar.markdown('### Cury company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""____""")

# Criando um slider para selecionar uma data
min_value = datetime(2022, 2, 11)
max_value = datetime(2022, 4, 6)
default_value = datetime(2022, 4, 1)

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=default_value,
    min_value=min_value,
    max_value=max_value,
    format="DD/MM/YYYY"
)

# Exibindo a data selecionada
st.header(f"Data selecionada: {date_slider.strftime('%d/%m/%Y')}")



st.sidebar.markdown("""----""")

trafego_configuracoes = st.sidebar.multiselect(
    "Quais as condições do trânsito ?", 
    [ 'Low' ,  'Medium' ,  'High' ,  'Jam' ],
    default = ['Low' , 'High' , 'Medium' , 'Jam' ] )
st.sidebar.markdown("""----""")
#filtro de data funcionando
linhas_selecionas = df1['Order_Date'] < date_slider
df1 = df1.loc[ linhas_selecionas , :]
# filtro de transito funcionando 
linhas_selecionas_transito = df1['Road_traffic_density'].isin( trafego_configuracoes )
df1 = df1.loc[ linhas_selecionas_transito , :]

#foto eu 
st.sidebar.markdown('### Feito por Gustavo Grecov')
image_path = "C:/Users/greco/Trabalho/portifolio/foto eu.jpg"
image = Image.open(image_path)
######################################################################################################################
# Exibindo no sidebar
st.sidebar.image(image, width=150) 

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])
with tab1:
    st.title("Overal Metrics")

    # Primeiro container - Linha 1
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            delivery_unique = len(df1['Delivery_person_ID'].unique())
            st.metric('Entregadores únicos', delivery_unique)

        with col2:
            from haversine import haversine
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                    'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1[cols].apply(lambda x: 
                haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                          (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                axis=1)
            avg_distance = np.round(df1['distance'].mean(), 2)
            st.metric('A distância média', avg_distance, 'Km')

        with col3:
            df_aux = df1.groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            tempo_festival = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'].values[0], 2)
            st.metric('Tempo Médio de entrega C/ festival', tempo_festival)

    # Segundo container - Linha 2
    with st.container():
        col4, col5, col6 = st.columns(3)

        with col4:
            std_festival = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'].values[0], 2)
            st.metric('Desvio Padrão de entrega C/ festival', std_festival)

        with col5:
            tempo_sem_festival = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'].values[0], 2)
            st.metric('Tempo de entrega S/ festival', tempo_sem_festival)

        with col6:
            std_sem_festival = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'].values[0], 2)
            st.metric('Desvio Padrão da entrega', std_sem_festival)
# Container de cima: gráfico de barra
with st.container():
    st.markdown("""-----""")
    st.title("Tempo Médio de Entrega por Cidade")

    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
            'Restaurant_latitude', 'Restaurant_longitude']

    df1['distance'] = df1.loc[:, cols].apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ),
        axis=1
    )

    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

    pastel_colors = ['#AEC6CF', '#FFB347', '#BFD8B8']
with st.container():
    st.markdown("""-----""")

    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({
        'Time_taken(min)': ['mean', 'std']
    })
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Tempo Médio',
        x=df_aux['City'],
        y=df_aux['avg_time'],
        error_y=dict(type='data', array=df_aux['std_time']),
        marker_color='#FFCCCB'
    ))
    st.plotly_chart(fig, key="bar_time_city")

    col1, col2 = st.columns(2)

    with col1:
        st.title("Tempo Médio de Entrega por Cidade")
        fig = go.Figure(data=[go.Pie(
            labels=avg_distance['City'],
            values=avg_distance['distance'],
            pull=[0, 0.1, 0],
            marker=dict(colors=pastel_colors)
        )])
        st.plotly_chart(fig, key="pie_bottom")

    with col2:
        st.title("Tempo Médio por Tráfego e Cidade")
        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({
            'Time_taken(min)': ['mean', 'std']
        })
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        fig = px.sunburst(
            df_aux, 
            path=['City', 'Road_traffic_density'], 
            values='avg_time',
            color='std_time',
            color_continuous_scale=['#F6BDC0', '#F0D9FF', '#B5EAD7'],
            color_continuous_midpoint=np.average(df_aux['std_time'])
        )
        st.plotly_chart(fig, key="sunburst_traffic")

with st.container():
    st.markdown("""-----""")
    with st.container():
        st.title("Distribuição da Distância")
    
        df_aux = (
            df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
            .groupby(['City', 'Type_of_order'])
            .agg({'Time_taken(min)': ['mean', 'std']})
        )
    
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
    
        st.dataframe(df_aux)


