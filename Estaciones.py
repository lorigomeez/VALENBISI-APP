# -*- coding: utf-8 -*-
"""MAPA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1faAWi_Tsz_DfhFB7ZIMocOOR8oWSWJg6
"""

#pip install selenium

#pip install webdriver_manager

import re
import requests
import zipfile
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
    df_estaciones = pd.read_csv(""https://github.com/lorigomeez/VALENBISI-APP/solo_coordenadas.csv")  # Reemplaza "archivo.csv" con el nombre de tu archivo CSV
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
