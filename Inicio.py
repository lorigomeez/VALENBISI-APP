# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 21:44:23 2023

@author: Usuario
"""

import streamlit as st
import Predicción
import Estaciones más cercanas

import pandas as pd
import requests
import zipfile
import requests
import io

def mostrar_prediccion():
    import streamlit as st
    import pandas as pd
    import requests
    from sklearn.compose import make_column_transformer
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.linear_model import LinearRegression
    
    
    url = 'https://github.com/lorigomeez/VALENBISI-APP/raw/main/valenbisi_procesado_coordenadas.zip'
    response = requests.get(url)
    
    # Leer el contenido del archivo comprimido en un objeto ZipFile
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    
    # Extraer el nombre del archivo CSV dentro del archivo comprimido
    csv_file_name = zip_file.namelist()[0]
    
    # Leer el archivo CSV dentro del archivo comprimido y cargarlo en un DataFrame
    df = pd.read_csv(zip_file.open(csv_file_name))
    
    #CREAR MODELO
    # Seleccionar las variables relevantes para la predicción
    variables = ['Dia', 'Mes', 'Año', 'Hora','name']
    target = ['avg_av','avg_free', 'avg_total']
    
    # Realizar codificación one-hot para la variable "name"
    name_encoder = OneHotEncoder(sparse=False)
    column_transformer = make_column_transformer((name_encoder, ['name']), remainder='passthrough')
    data_encoded = column_transformer.fit_transform(data[variables])
    
    # Obtener los nombres de las características después de la codificación one-hot
    name_categories = list(column_transformer.named_transformers_['onehotencoder'].categories_[0])
    feature_names = name_categories + variables[1:]
    
    # Crear el conjunto de datos de entrenamiento
    X = data_encoded
    y = data[target]
    
    # Crear el modelo de regresión lineal
    model = LinearRegression()
    
    # Entrenar el modelo
    model.fit(X, y)
    
    
    st.title("Predicción de disponibilidad")
    
    
    
    Hora = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ,13,14,15,16,17,18,19,20,21,22,23]
    Dia = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
    Mes = [1,2,3,4,5,6,7,8,9,10,11,12]
    Nombre=list(data['name'].unique())
    Anyo = [2023,2024]
    graficos = ['Bicicletas disponibles', 'Espacios libres']
    
    with st.form('entry_form', clear_on_submit = False):
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Selecciona día:" , Dia, key="day")
        col2.selectbox("Selecciona mes:" , Mes, key="month")
        col3.selectbox("Selecciona año:" , Anyo, key="year")
        col1.selectbox("Selecciona hora:" , Hora, key="hour")
        col2.selectbox("¿Qué quieres predecir?", graficos, key='figure')
        col3.selectbox('Selecciona estación: ', Nombre, key = 'name')
        submitted = st.form_submit_button(label='Guardar datos')
        if submitted:
            selected_day = st.session_state.day
            selected_month = st.session_state.month
            selected_year = st.session_state.year
            selected_hour = st.session_state.hour
            selected_name = st.session_state.name
            selected_figure = st.session_state.figure
            
    
            st.success('Datos guardados')
    
            
            if selected_figure == 'Bicicletas disponibles':
                nuevos_datos = pd.DataFrame([[selected_day, selected_month, selected_year, selected_hour, selected_name]], columns=variables)
                nuevos_datos_encoded = column_transformer.transform(nuevos_datos)
                
                # Realizar la predicción
                prediccion = model.predict(nuevos_datos_encoded)
                
                #avg_av
                st.write("Media de bicicletas disponibles: ", round(prediccion[0][0]))
    
                
                
    
            if selected_figure == 'Espacios libres':
                nuevos_datos = pd.DataFrame([[selected_day, selected_month, selected_year, selected_hour, selected_name]], columns=variables)
                nuevos_datos_encoded = column_transformer.transform(nuevos_datos)
                
                # Realizar la predicción
                prediccion = model.predict(nuevos_datos_encoded)
                
                # Mostrar la predicción
                st.subheader("Resultados de la predicción:")
                st.write(prediccion)
                
                #avg_av
                st.write("Media de espacios libres: ",prediccion[0][1])
    
    
def mostrar_mapa():
    import re
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import streamlit as st
    
    page_title = 'ESTACIONES MÁS CERCANAS'
    layout = 'wide'
    
    st.set_page_config(page_title = page_title, layout = layout)
    
    st.title(page_title)
    
    direccion = st.text_input('Introduce una dirección: (Ejemplo: Calle Eugenia Viñes 40, Valencia)', '')
    submit_button = st.button('Enviar')
    
    # Verificar si se hizo clic en el botón de envío
    if submit_button:
    
        st.write('Dirección ingresada:', direccion)
        
        ## OBTENER COORDENADAS
        
        # Configuración de Selenium para usar Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecución sin abrir ventana del navegador
        #driver = webdriver.Chrome(options=chrome_options)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        # URL de la página web
        url = "https://www.coordenadas-gps.com/convertidor-de-coordenadas-gps"
        
        # Obtener datos del usuario
        #direccion = input("Introduce una dirección: ")
        
        # Navegar a la página web
        driver.get(url)
        
        # Esperar a que la página se cargue completamente
        driver.implicitly_wait(10)
        
        # Introducir los datos del municipio y calle/número en los campos correspondientes
        input_direccion = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[1]/form[1]/div[1]/div/input")
        input_direccion.send_keys(direccion)
        
        
        # Hacer clic en el botón de búsqueda
        boton_buscar = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[1]/form[1]/div[2]/div/button")
        boton_buscar.click()
        
        # Esperar a que se carguen los resultados
        driver.implicitly_wait(6)
        
        # Obtener las coordenadas EPSG
        info = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[2]/div/div[4]/div[2]/table")
        
        # Obtener todas las filas de la tabla
        filas = info.find_elements(By.TAG_NAME, "tr")
        
        info2 = []
        # Iterar sobre cada fila y obtener los datos de las celdas
        for fila in filas:
            # Obtener todas las celdas de la fila
            celdas = fila.find_elements(By.TAG_NAME, "td")
            
            # Obtener el texto de cada celda e imprimirlo
            for celda in celdas:
                texto_celda = celda.text
                info2.append(texto_celda)
        
        latitud = float(info2[1])
        longitud = float(info2[2])
        
        
        coordenadas = [float(latitud), float(longitud)]
        
        print(coordenadas)
        
        # Cerrar el navegador
        driver.quit()
        
        
        ## COMPARAR COORDENADAS (ENCONTRAR LAS ESTACIONES MÁS CERCANAS)
        from geopy.distance import geodesic
        import pandas as pd
        import folium
        
        # Coordenadas de referencia
        tu_latitud = latitud
        tu_longitud = longitud
        
        # DataFrame con las estaciones
        df_estaciones = pd.read_csv("C:/Users/Usuario/Desktop/UNI/EDM/trabajo/primavera/solo_coordenadas.csv")  # Reemplaza "archivo.csv" con el nombre de tu archivo CSV
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

opciones_paginas = ["Estaciones más cercanas", "Predicción"]
opcion_seleccionada = st.sidebar.radio("Selecciona una página", opciones_paginas)
if opcion_seleccionada == "Predicción":
    mostrar_prediccion()
elif opcion_seleccionada == "Estaciones más cercanas":
    mostrar_mapa()

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


        
        
        
        
