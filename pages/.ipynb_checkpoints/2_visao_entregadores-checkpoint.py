
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st 
from datetime import datetime
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="🚲" 
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
print (df1)
import streamlit as st
import pandas as pd
from datetime import datetime

# Visão Empresa
st.header('Marketplace - Visão Entregadores')

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

# Exibindo no sidebar
st.sidebar.image(image, width=150) 
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    # MÉTRICAS GERAIS
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

    # AVALIAÇÕES
    with st.container():
        st.markdown("""-----""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings_per_deliver = df1[['Delivery_person_Ratings', 'Delivery_person_ID']] \
                .groupby('Delivery_person_ID') \
                .mean() \
                .reset_index()
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown('##### Avaliação média por trânsito (tabela)')
            colsc = ['Delivery_person_Ratings', 'Road_traffic_density']
            dfe = df1[colsc].groupby('Road_traffic_density').agg(['mean', 'std']).reset_index()
            dfe.columns = ['Trânsito', 'Média de Avaliação', 'Desvio Padrão']
            st.dataframe(dfe)

import plotly.express as px
import plotly.graph_objects as go

# ========================
# Agrupamentos necessários
# ========================

# Avaliação por trânsito
colsc = ['Delivery_person_Ratings', 'Road_traffic_density']
dfe = df1.loc[:, colsc] \
    .groupby('Road_traffic_density') \
    .agg(['mean', 'std']) \
    .reset_index()
dfe.columns = ['Trânsito', 'Média de Avaliação', 'Desvio Padrão']

# Avaliação por clima
dfc = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']] \
    .groupby('Weatherconditions') \
    .agg(['mean', 'std']) \
    .reset_index()
dfc.columns = ['Condições Climáticas', 'Média de Avaliação', 'Desvio Padrão']

# ========================
# Estilo personalizado
# ========================

custom_template = dict(
    layout=go.Layout(
        plot_bgcolor="#f7f7f7",
        paper_bgcolor="#ffffff",
        font=dict(color="#333", size=12),
        xaxis=dict(showgrid=True, gridcolor="#e6e6e6", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#e6e6e6", zeroline=False),
    )
)

# ========================
# Gráficos
# ========================

# Gráfico de linha - Avaliação por trânsito
with st.container():
    st.markdown("##### Avaliação média por trânsito")
    fig_trafego = px.line(
        dfe,
        x='Trânsito',
        y='Média de Avaliação',
        error_y='Desvio Padrão',
        color='Trânsito',
        markers=True,
        template=custom_template,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_trafego.update_traces(line=dict(width=3))
    st.plotly_chart(fig_trafego, use_container_width=True)

# Gráfico de linha - Avaliação por clima
with st.container():
    st.markdown("##### Avaliação média por clima")
    fig_clima = px.line(
        dfc,
        x='Condições Climáticas',
        y='Média de Avaliação',
        error_y='Desvio Padrão',
        color='Condições Climáticas',
        markers=True,
        template=custom_template,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_clima.update_traces(line=dict(width=3))
    st.plotly_chart(fig_clima, use_container_width=True)

    # VELOCIDADE DE ENTREGA
    with st.container():
        st.markdown("""-----""")
        st.title('Velocidade de Entregas')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df2 = df1[['Delivery_person_ID', 'Time_taken(min)', 'City']] \
                .groupby(['City', 'Delivery_person_ID']) \
                .min() \
                .sort_values(['City', 'Time_taken(min)']) \
                .reset_index()
            df2_aux1 = df2[df2['City'] == 'Metropolitian'].head(10)
            df2_aux2 = df2[df2['City'] == 'Urban'].head(10)
            df2_aux3 = df2[df2['City'] == 'Semi-Urban'].head(10)
            df2_fastest = pd.concat([df2_aux1, df2_aux2, df2_aux3]).reset_index(drop=True)
            st.dataframe(df2_fastest)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df2 = df1[['Delivery_person_ID', 'Time_taken(min)', 'City']] \
                .groupby(['City', 'Delivery_person_ID']) \
                .min() \
                .sort_values(['City', 'Time_taken(min)'], ascending=False) \
                .reset_index()
            df2_aux1 = df2[df2['City'] == 'Metropolitian'].head(10)
            df2_aux2 = df2[df2['City'] == 'Urban'].head(10)
            df2_aux3 = df2[df2['City'] == 'Semi-Urban'].head(10)
            df2_slowest = pd.concat([df2_aux1, df2_aux2, df2_aux3]).reset_index(drop=True)
            st.dataframe(df2_slowest)



