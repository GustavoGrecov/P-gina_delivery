import pandas as pd
import plotly.express as px
import streamlit as st 
from datetime import datetime
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import streamlit as st
from datetime import datetime
st.set_page_config(
    page_title="Visão Empresa",
    page_icon="🏢" 
)

#import dataset 
df = pd.read_csv("C:/Users/greco/Trabalho/portifolio/train.csv")
#limpando o dataset
df1 = df.copy()


#---------------------------------------------
#FUNÇÕES
#---------------------------------------------
# 1. Gráfico de Pedidos por Tipo de Tráfego
def pedidos_por_trafego(df1):
    dfx = df1.loc[:, ['Road_traffic_density', 'ID']] \
        .groupby(['Road_traffic_density']).count().reset_index()
    dfx['entregas_perc'] = dfx['ID'] / dfx['ID'].sum()
    fig = px.pie(dfx,
                 values='entregas_perc',
                 names='Road_traffic_density',
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 template=custom_template,
                 hole=0.4)
    return fig

# 2. Gráfico de Pedidos por Dia
def pedidos_por_dia(df1):
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.line(df_aux,
                  x='Order_Date',
                  y='ID',
                  markers=True,
                  template=custom_template,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=3))
    return fig

# 3. Gráfico de Volume de Pedidos por Cidade e Tráfego
def pedidos_cidade_trafego(df1):
    dfx = df1.loc[:, ['ID', 'City', 'Road_traffic_density']] \
        .groupby(['City', 'Road_traffic_density']).count().reset_index()
    dfx['perc_ID'] = 100 * (dfx['ID'] / dfx['ID'].sum())
    fig = px.bar(dfx,
                 x='City',
                 y='ID',
                 color='Road_traffic_density',
                 barmode='group',
                 template=custom_template,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    return fig

# 4. Gráfico de Pedidos por Semana
def pedidos_por_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']] \
        .groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux,
                  x='week_of_year',
                  y='ID',
                  markers=True,
                  template=custom_template,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=3))
    return fig

# 5. Gráfico de Pedidos por Entregador por Semana
def pedidos_por_entregador_por_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']] \
        .groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']] \
        .groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux,
                  x='week_of_year',
                  y='order_by_deliver',
                  markers=True,
                  template=custom_template,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=3))
    return fig

    import folium
from streamlit_folium import folium_static

def mapa_entregas(df1):
    df_filtrado = df1.query('Distancia <= 100').copy()
    df_sample = df_filtrado.sample(50)

    # Centralizar o mapa no primeiro restaurante
    map_center = [df_sample['Restaurant_latitude'].iloc[0], df_sample['Restaurant_longitude'].iloc[0]]
    mapa = folium.Map(location=map_center, zoom_start=4)

    for _, row in df_sample.iterrows():
        # Restaurante
        folium.Marker(
            location=[row['Restaurant_latitude'], row['Restaurant_longitude']],
            popup='Restaurante',
            icon=folium.Icon(color='blue')
        ).add_to(mapa)

        # Local de entrega
        folium.Marker(
            location=[row['Delivery_location_latitude'], row['Delivery_location_longitude']],
            popup='Entrega',
            icon=folium.Icon(color='lightgreen')
        ).add_to(mapa)

        # Linha conectando os dois pontos
        folium.PolyLine(
            locations=[
                [row['Restaurant_latitude'], row['Restaurant_longitude']],
                [row['Delivery_location_latitude'], row['Delivery_location_longitude']]
            ],
            color='red',
            weight=3
        ).add_to(mapa)

    return mapa

def clean_code( df1 ):
    """" Esta função tem a responsabilidade de limpar o dataframe
    tipos de limpeza:
    1 remoção dos dados NAN 
    2 mudança do tipo da coluna 
    3 remoção dos espaços das variaveis 
    4 formatação da data 
    5 limpeza da coluna de tempo
    input: Dataframe
    output: Dataframe 
    """
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
    # Remover "(min)" e espaços extras, depois converter para número
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.extract(r'(\d+)').astype(float)
    
    return df1

#----------------------------------------------------- FIM -----------------------------------------------------------


#limpando os dados 
df1 = clean_code (df1)
    
def calcular_distancia(row):
    ponto_restaurante = (row['Restaurant_latitude'], row['Restaurant_longitude'])
    ponto_entrega = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
    return geodesic(ponto_restaurante, ponto_entrega).kilometers
df1['Distancia'] = df1.apply(calcular_distancia, axis=1 )

#___________________________________inicio da estrutura lógica do código _________________

# Visão Empresa
st.header('Marketplace - Visão Empresa')

#====================================================
# BARRA LATERAL 
#====================================================
# ==============================
# 🎛️ BARRA LATERAL COM VISUAL SUAVE
# ==============================
image_path2 = "C:/Users/greco/Trabalho/portifolio/foto_delivery.jpg"
image = Image.open(image_path2)
st.sidebar.image(image, width=120)
st.sidebar.markdown("*O mais rapido Delivery da cidade*")

st.sidebar.markdown("""<hr style='margin-top:0; margin-bottom:0;'>""", unsafe_allow_html=True)

# 📅 Slider de data com legenda estilizada
st.sidebar.markdown("#### 📅 Filtrar pedidos até a data:")
min_value = datetime(2022, 2, 11)
max_value = datetime(2022, 4, 6)
default_value = datetime(2022, 4, 1)

date_slider = st.sidebar.slider(
    label='',
    value=default_value,
    min_value=min_value,
    max_value=max_value,
    format="DD/MM/YYYY"
)

st.sidebar.markdown("""<hr style='margin-top:0; margin-bottom:0;'>""", unsafe_allow_html=True)

# 🚦 Seleção de condições de trânsito com cores leves
st.sidebar.markdown("#### 🚦 Selecionar condições de trânsito:")
trafego_configuracoes = st.sidebar.multiselect(
    label='',
    options=['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""<hr style='margin-top:0; margin-bottom:0;'>""", unsafe_allow_html=True)

# 👤 Autor
st.sidebar.markdown("### 👨‍💻 Feito por Gustavo Grecov")
image_path = "C:/Users/greco/Trabalho/portifolio/foto eu.jpg"
image = Image.open(image_path)
st.sidebar.image(image, width=150)

# ==============================
# 🌤️ Cabeçalho com data filtrada
# ==============================
st.markdown(f"### 📆 Data selecionada: `{date_slider.strftime('%d/%m/%Y')}`")

# ==============================
# 📊 Aplicando filtros no DataFrame
# ==============================
df1 = df1[df1['Order_Date'] < date_slider]
df1 = df1[df1['Road_traffic_density'].isin(trafego_configuracoes)]

#====================================================
# layout central
#====================================================
import plotly.express as px
import plotly.graph_objects as go

# Template de visualização com cores suaves
custom_template = dict(
    layout=go.Layout(
        plot_bgcolor="#f7f7f7",
        paper_bgcolor="#ffffff",
        font=dict(color="#333", size=12),
        xaxis=dict(showgrid=True, gridcolor="#e6e6e6", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#e6e6e6", zeroline=False),
    )
)

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# ============================
# TAB 1 - Visão Gerencial
# ============================
with tab1:
    with st.container():  # 1. Quantidade de pedidos por dia.
        st.markdown('### 📅 Pedidos por Dia')
        fig = pedidos_por_dia(df1)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""---""")

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

# ============================
# TAB 2 - Visão Tática
# ============================
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
        st.markdown('### 🗺️ Mapa de pedidos com distância até o destino')
        mapa = mapa_entregas(df1)
        folium_static(mapa, width=1024, height=600)


        







    

