import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏠" 
)

image_path2 = "C:/Users/greco/Trabalho/portifolio/foto_delivery.jpg"
image = Image.open(image_path2)
st.sidebar.image(image, width=120)
st.sidebar.markdown("*O mais rapido Delivery da cidade*")
st.write("# Dashboard da Express Delivery")
st.markdown(
    '''
Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
### Como utilizar esse Growth Dashboard?
- Visão Empresa:
    - Visão Gerencial: Métricas gerais de comportamento.
    - Visão Tática: Indicadores semanais de crescimento.
    - Visão Geográfica: Insights de geolocalização.

- Visão Entregador:
    - Acompanhamento dos indicadores semanais de crescimento

- Visão Restaurante:
    - Indicadores semanais de crescimento dos restaurantes

### Ask for Help
- Time de Data Science no LinkedIn 
    - linkedin.com/in/gustavo-sales-grecov-530745350/

''')