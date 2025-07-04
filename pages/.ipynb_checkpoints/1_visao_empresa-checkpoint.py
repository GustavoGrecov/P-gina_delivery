import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

st.set_page_config(
    page_title="Visão Empresa",
    page_icon="🏢"
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
    # Remoção dos dados NaN e conversão de tipos
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

    # Remoção dos espaços das variáveis
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # Limpeza da coluna de tempo
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.extract(r'(\d+)').astype(float)
    
    # Criação da coluna da semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    # <<< CORREÇÃO: Cálculo da distância movido para dentro da função de limpeza
    def calcular_distancia(row):
        ponto_restaurante = (row['Restaurant_latitude'], row['Restaurant_longitude'])
        ponto_entrega = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
        return geodesic(ponto_restaurante, ponto_entrega).kilometers
    df1['Distancia'] = df1.apply(calcular_distancia, axis=1)

    return df1

def pedidos_por_trafego(df1):
    dfx = df1.loc[:, ['Road_traffic_density', 'ID']].groupby(['Road_traffic_density']).count().reset_index()
    dfx['entregas_perc'] = dfx['ID'] / dfx['ID'].sum()
    fig = px.pie(dfx, values='entregas_perc', names='Road_traffic_density', color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.4)
    return fig

def pedidos_por_dia(df1):
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.line(df_aux, x='Order_Date', y='ID', markers=True, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=3))
    return fig

def pedidos_cidade_trafego(df1):
    dfx = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(dfx, x='City', y='Road_traffic_density', size='ID', color='City', color_discrete_sequence=px.colors.qualitative.Pastel)
    return fig

def pedidos_por_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID', markers=True, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=3))
    return fig

def pedidos_por_entregador_por_semana(df1):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver', markers=True, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=3))
    return fig

def mapa_entregas(df1):
    df_filtrado = df1.query('Distancia <= 100').copy()
    df_sample = df_filtrado.sample(50)
    map_center = [df_sample['Restaurant_latitude'].iloc[0], df_sample['Restaurant_longitude'].iloc[0]]
    mapa = folium.Map(location=map_center, zoom_start=4)
    for _, row in df_sample.iterrows():
        folium.Marker(location=[row['Restaurant_latitude'], row['Restaurant_longitude']], popup='Restaurante', icon=folium.Icon(color='blue')).add_to(mapa)
        folium.Marker(location=[row['Delivery_location_latitude'], row['Delivery_location_longitude']], popup='Entrega', icon=folium.Icon(color='lightgreen')).add_to(mapa)
        folium.PolyLine(locations=[[row['Restaurant_latitude'], row['Restaurant_longitude']], [row['Delivery_location_latitude'], row['Delivery_location_longitude']]], color='red', weight=3).add_to(mapa)
    return mapa

# =============================================
# INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
# =============================================
# <<< CORREÇÃO: Usando caminho relativo
df_raw = load_data('train.csv')
df1 = clean_code(df_raw.copy())

# Visão Empresa
st.header('Marketplace - Visão Empresa')

# ==============================
# BARRA LATERAL
# ==============================
# <<< CORREÇÃO: Usando caminho relativo
image_path2 = "foto_delivery.jpg"
image = Image.open(image_path2)
st.sidebar.image(image, width=120)

st.sidebar.markdown("*O mais rapido Delivery da cidade*")
st.sidebar.markdown("""---""")

st.sidebar.markdown("#### 📅 Filtrar pedidos até a data:")
date_slider = st.sidebar.slider(
    label='Selecione uma data',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="DD/MM/YYYY"
)
st.sidebar.markdown("""---""")

st.sidebar.markdown("#### 🚦 Selecionar condições de trânsito:")
trafego_configuracoes = st.sidebar.multiselect(
    label='Quais as condições?',
    options=['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown("""---""")

# <<< CORREÇÃO: Usando caminho relativo
st.sidebar.markdown("### 👨‍💻 Feito por Gustavo Grecov")
image_path = "foto eu.jpg"
image_autor = Image.open(image_path)
st.sidebar.image(image_autor, width=150)

# Aplicando filtros no DataFrame
df1 = df1[df1['Order_Date'] < date_slider]
df1 = df1[df1['Road_traffic_density'].isin(trafego_configuracoes)]

# ==============================
# LAYOUT CENTRAL
# ==============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('### 📅 Pedidos por Dia')
        fig = pedidos_por_dia(df1)
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### 🚦 Pedidos por Tipo de Tráfego')
            fig = pedidos_por_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('### 🏙️ Volume de Pedidos por Cidade e Tráfego')
            fig = pedidos_cidade_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('### 📈 Pedidos por Semana')
        fig = pedidos_por_semana(df1)
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        st.markdown('### 📊 Pedidos por Entregador por Semana')
        fig = pedidos_por_entregador_por_semana(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    with st.container():
        st.markdown('### 🗺️ Mapa de entregas')
        mapa = mapa_entregas(df1)
        folium_static(mapa, width=1024, height=600)