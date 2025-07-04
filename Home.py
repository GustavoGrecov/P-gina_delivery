import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏠" 
)

# --- CORREÇÃO: Usando caminho relativo para a imagem ---
try:
    image = Image.open("foto_delivery.jpg")
    st.sidebar.image(image, width=120)
except FileNotFoundError:
    st.sidebar.error("Imagem 'foto_delivery.jpg' não encontrada. Verifique se ela está no repositório do GitHub.")

st.sidebar.markdown("*O mais rapido Delivery da cidade*")
st.sidebar.markdown("---")
st.sidebar.markdown("### Feito por Gustavo Grecov")

st.write("# Dashboard da Express Delivery 📈")
st.markdown(
    """
    O Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    
    ### Como utilizar esse Growth Dashboard?
    - **Visão Empresa:**
        - **Visão Gerencial:** Métricas gerais de comportamento.
        - **Visão Tática:** Indicadores semanais de crescimento.
        - **Visão Geográfica:** Insights de geolocalização.
    - **Visão Entregador:**
        - Acompanhamento dos indicadores semanais de crescimento.
    - **Visão Restaurante:**
        - Indicadores semanais de crescimento dos restaurantes.
    
    ### Precisa de ajuda?
    - **Time de Data Science no LinkedIn**
        - [Gustavo Sales Grecov](https://www.linkedin.com/in/gustavo-sales-grecov-530745350/)
    """
)

