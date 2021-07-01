# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 18:26:28 2021

@author: aranc
"""


import streamlit as st
import pandas as pd
import base64
import requests
import datetime
from io import BytesIO

## TITULO Y CUERPO DE LA PÁGINA ###

st.write("""
# Fantasy Premier League Data Exploration


For Premier League 2020 - 2021.


Check players' points in each gameweek, using data from the FantasyPL API.


More info about the [game](https://fantasy.premierleague.com/).

         """)
         
st.markdown("""
            
* **Python libraries:** pandas, streamlit, base64
* **Data sources: ** endpoints are [bootstrap-static](https://fantasy.premierleague.com/api/bootstrap-static/),
                    [element-id (each player has an id)](https://fantasy.premierleague.com/api/element-summary/{element_id}/)
* **Github: ** [Github repository](https://github.com/juarancibi/fpldata_heroku)
            """)



url = 'https://fantasy.premierleague.com/api/bootstrap-static/'                                    ## ENDPOINT DE DONDE SACO LA INFO RELEVANTE
r = requests.get(url)                                                            
json = r.json()                                                                  
json.keys()

st.write('FPL 20/21 is closed, FPL 21/22 starts August 13.') 

url2 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/pointsbygw.csv'           ## URL DEL ARCHIVO EN GITHUB, TABLA CREADA POR OTRO ARCHIVO PYTHON
testGraph2 = pd.read_csv(url2,index_col=0)

##SLIDER##
slider_1, slider_2 = st.sidebar.slider("Gameweek", 1, 38,(1, 38))                  ## SELECCIONA TODOS LOS GAMEWEEKS ACTUALES POR DEFECTO

testGraph3 = testGraph2.iloc[:, slider_1-1:slider_2]                                               ## GENERA DATAFRAME CON LOS GAMEWEEKS SELECCIONADOS EN LA PÁGINA
#testGraph3['Total Points'] =  testGraph3.sum(axis=1)                                               ## SUMA TODOS LOS GAMEWEEKS Y GENERA LA COLUMNA 'TOTAL POINTS'

url3 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/lastseason.csv'           ## URL DEL ARCHIVO EN GITHUB CON LOS PUNTOS SACADOS EN LA TEMPORADA PASADA
lstseasongraph = pd.read_csv(url3, index_col=0)                                                    
lastseasonpoints = list(lstseasongraph.iloc[:,0])                                                  ## GENERA LISTA CON LOS PUNTOS DE CADA JUGADOR TEMPORADA PASADA

##MULTISELECT##
sorted_unique_team = sorted(testGraph3.team.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)             ## SELECCIONA TODOS LOS EQUIPOS EN ORDEN ALFABÉTICO

##MULTISELECT##
unique_pos = ['Goalkeeper','Defender','Midfielder','Forward']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)                          ## SELECCIONA TODOS LAS POSICIONES

df_selected_team = testGraph3[(testGraph3.team.isin(selected_team)) & (testGraph3.position.isin(selected_pos))]               ## CREO UN DATAFRAME QUE FILTRA TABLA CON RESPECTO AL INPUT EN LA PAGINA DE EQUIPOS Y POSICIONES QUE SE SELECCIONEN                                                                                                      

st.dataframe(testGraph3)                                                                             ## MUESTRA EL DATAFRAME FINAL EN LA PÁGINA


### DESCARGA EN CSV ###

def filedownload(df):                                                   
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerpoints.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(final_df), unsafe_allow_html=True)
