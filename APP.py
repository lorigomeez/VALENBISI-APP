# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 21:44:23 2023

@author: Usuario
"""

import streamlit as st


import pandas as pd
import requests
import zipfile
import requests
import io

#GENERAL
url = 'https://github.com/lorigomeez/VALENBISI-APP/raw/main/valenbisi_procesado_coordenadas.zip'
response = requests.get(url)

# Leer el contenido del archivo comprimido en un objeto ZipFile
zip_file = zipfile.ZipFile(io.BytesIO(response.content))

# Extraer el nombre del archivo CSV dentro del archivo comprimido
csv_file_name = zip_file.namelist()[0]

# Leer el archivo CSV dentro del archivo comprimido y cargarlo en un DataFrame
df = pd.read_csv(zip_file.open(csv_file_name))

page_title = 'VALENBISI Datos históricos'
layout = 'wide'

st.set_page_config(page_title = page_title, layout = layout)

st.title(page_title)

Hora = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ,13,14,15,16,17,18,19,20,21,22,23]
Dia = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
Mes = [1,2,3,4,5,6,7,8,9,10,11,12]
Anyo = [2022,2023]
graficos = ['Bicicletas disponibles', 'Espacios libres disponibles', 'Estaciones cerradas']

st.write('Selecciona un día, mes, año y hora, y haz click en Guardar datos.')
with st.form('entry_form', clear_on_submit = False):
    col1, col2, col3, col4 = st.columns(4)
    col1.selectbox("Selecciona día:" , Dia, key="day")
    col2.selectbox("Selecciona mes:" , Mes, key="month")
    col3.selectbox("Selecciona año:" , Anyo, key="year")
    col4.selectbox("Selecciona hora:" , Hora, key="hour")
    col1.selectbox("¿Qué quieres ver? ", graficos, key='figure')
    
    "---"
    submitted = st.form_submit_button('Guardar datos')
    if submitted:
        selected_day = st.session_state.day
        selected_month = st.session_state.month
        selected_year = st.session_state.year
        selected_hour = st.session_state.hour
        selected_figure = st.session_state.figure

        st.success('Datos guardados')

        st.header('Resultado')
        
        if selected_figure == 'Bicicletas disponibles':
            df_filtrado = df[(df['Mes'] == selected_month) & (df['Dia'] == selected_day) & (df['Hora'] == selected_hour) & (df['Año'] == selected_year)]
            df_top_10 = df_filtrado.sort_values(by='avg_av', ascending=False).head(10)
            import plotly.express as px
            fig = px.bar(df_top_10, x='name', y='avg_av',
                         color='avg_av',
                         labels={'name': 'Estación', 'avg_av': 'Media de bicis disponibles'},
                         title=f'Las 10 estaciones con más bicis disponibles para los datos introducidos')
            fig.update_layout(margin = dict(l=0, r=0, t =30, b = 5))
            st.plotly_chart(fig, use_container_width=True)
            
            

        if selected_figure == 'Espacios libres disponibles':
            df_filtrado = df[(df['Mes'] == selected_month) & (df['Dia'] == selected_day) & (df['Hora'] == selected_hour) & (df['Año'] == selected_year)]
            df_top_10 = df_filtrado.sort_values(by='avg_free', ascending=False).head(10)
            import plotly.express as px
            fig = px.bar(df_top_10, x='name', y='avg_free',
                         color='avg_free',
                         labels={'name': 'Estación', 'avg_free': 'Media de espacios libres'},
                         title=f'Las 10 estaciones con más espacios libres disponibles para los datos introducidos')
            fig.update_layout(margin = dict(l=0, r=0, t =30, b = 5))
            st.plotly_chart(fig, use_container_width=True)


        if selected_figure == 'Estaciones cerradas':
            st.write('Estaciones cerradas')
            datos = df[(df['open'] == 'F') & (df['Mes'] == selected_month) & (df['Dia'] == selected_day) & (df['Hora'] == selected_hour) & (df['Año'] == selected_year)]
            datos = datos[['name', 'address', 'number_']]
            datos = datos.rename(columns={'name': 'Estación', 'address': 'Dirección', 'number_': 'Número'})

            styles = [
    {"selector": "table", "props": [("border-collapse", "collapse")]},
    {"selector": "th, td", "props": [("border", "1px solid #ccc"), ("padding", "8px")]},
    {"selector": "th", "props": [("background-color", "#f2f2f2"), ("color", "#333")]}
]

            style_string = ""
            for style in styles:
                selector = style["selector"]
                props = "; ".join([f"{prop[0]}: {prop[1]}" for prop in style["props"]])
                style_string += f"{selector} {{ {props} }} "
            
            styled_table = f"<style>{style_string}</style>"
            st.markdown(styled_table, unsafe_allow_html=True)

            st.table(datos)


### MAPA
import zipfile
import streamlit as st


st.header('ESTACIONES MÁS CERCANAS')
st.write('Selecciona un punto en el mapa')
## OBTENER COORDENADAS
# Coordenadas iniciales de Valencia
initial_coords = (39.46975, -0.37739)

# Crear el mapa de Folium centrado en Valencia
mapa = folium.Map(location=initial_coords, zoom_start=13)

# Mostrar el mapa en Streamlit
folium_static(mapa)

# Obtener la ubicación seleccionada por el usuario
result = mapa.add_child(folium.LatLngPopup())

if result:
    selected_location = result.location
    latitud = selected_location[0]
    longitud = selected_location[1]
    
    ## COMPARAR COORDENADAS (ENCONTRAR LAS ESTACIONES MÁS CERCANAS)
    from geopy.distance import geodesic
    import pandas as pd
    import folium
        
    # Coordenadas de referencia
    tu_latitud = latitud
    tu_longitud = longitud   
        
    # DataFrame con las estaciones
    df_estaciones = pd.read_csv("https://github.com/lorigomeez/VALENBISI-APP/solo_coordenadas.csv")  # Reemplaza "archivo.csv" con el nombre de tu archivo CSV
    df_estaciones["distancia"] = df_estaciones.apply(
        lambda row: geodesic((tu_latitud, tu_longitud), (row["geo_point_2d"].split(',')[0], row["geo_point_2d"].split(',')[1])).kilometers,
        axis=1
    )
    df_estaciones_cercanas = df_estaciones.nsmallest(5, "distancia")
        
    # Imprimir las estaciones más cercanas
    #for index, row in df_estaciones_cercanas.iterrows():
    #print(row["name"])
        
        
    # MOSTRAR EN MAPA
    from streamlit_folium import folium_static
    import folium
    import streamlit as st
        
    # Crear el mapa de Folium centrado en la calle seleccionada
    mapa = folium.Map(location=[latitud, longitud], zoom_start=15)
        
    # Agregar marcador en la ubicación de la calle seleccionada
    folium.Marker(
        location=[latitud, longitud],
        icon=folium.Icon(color='blue', icon='info-sign', popup = direccion)
    ).add_to(mapa)
        
    # Agregar marcadores para las estaciones más cercanas
    for index, row in df_estaciones_cercanas.iterrows():
        folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=row['name'],
            icon=folium.Icon(color='red')
        ).add_to(mapa)
        
    st.markdown(
    """
    <style>
    .css-1aumxhk {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
    
    st.header('Mapa con las 5 estaciones más cercanas a la dirección introducida.')
    st.write('El marcador azul es la dirección introducida y los marcadores rojos son las estaciones más cercanas. Al pulsar sobre estos marcadores aparece los nombre de las estaciones.')
    folium_static(mapa)


    
    
