# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 18:26:28 2021

@author: aranc
"""


import streamlit as st
import pandas as pd
import base64
import requests
from io import BytesIO

## TITULO Y CUERPO DE LA PÁGINA ###

st.write("""
# Fantasy Premier League Data Exploration



Check players' points in each gameweek, using the FantasyPL API.


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


### DATAFRAMES RELEVANTES ###

events_df = pd.DataFrame(json['events'])
elements_df = pd.DataFrame(json['elements'])
elements_df = elements_df[['id','web_name','team','element_type','selected_by_percent','now_cost','minutes',
                                'transfers_in','value_season','total_points','event_points']]                      
teams_df = pd.DataFrame(json['teams'])
elements_types_df = pd.DataFrame(json['element_types'])


### TRANSFORMAR A LISTAS COLUMNAS IMPORTANTES DE LOS DATAFRAMES ###

teamList = list(elements_df.team)
positionList = list(elements_df.element_type)
eventpointsList = list(elements_df.event_points)


### DEVUELVE EL GAMEWEEK (FECHA) EN LA QUE SE ENCUENTRA LA PREMIER ###

current_gw = events_df.id[events_df['is_current'] == True].tolist()[0]
st.write('The current gameweek is Gameweek ' + str(current_gw))                                    ## MUESTRA EN LA PÁGINA LA FECHA ACTUAL DE LA PREMIER                                   


### LEE EL ARCHIVO CON LOS PUNTOS POR GAMEWEEK ###

url2 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/pointsbygw.csv'           ## URL DEL ARCHIVO EN GITHUB, TABLA CREADA POR OTRO ARCHIVO PYTHON
testGraph2 = pd.read_csv(url2,index_col=0)
testGraph2.drop(['id','team','position'], axis=1, inplace=True)
testGraph2['GW'+' '+str(current_gw)] = list(eventpointsList)


### ARREGLOS PARA EL DATAFRAME FINAL CON SLIDERS Y MULTISELECTS ###

##SLIDER##
slider_1, slider_2 = st.sidebar.slider("Gameweek", 1, current_gw,(1, current_gw))                  ## SELECCIONA TODOS LOS GAMEWEEKS ACTUALES POR DEFECTO

testGraph3 = testGraph2.iloc[:, slider_1-1:slider_2]                                               ## GENERA DATAFRAME CON LOS GAMEWEEKS SELECCIONADOS EN LA PÁGINA
testGraph3['Total Points'] =  testGraph3.sum(axis=1)                                               ## SUMA TODOS LOS GAMEWEEKS Y GENERA LA COLUMNA 'TOTAL POINTS'

url3 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/lastseason.csv'           ## URL DEL ARCHIVO EN GITHUB CON LOS PUNTOS SACADOS EN LA TEMPORADA PASADA
lstseasongraph = pd.read_csv(url3, index_col=0)                                                    
lastseasonpoints = list(lstseasongraph.iloc[:,0])                                                  ## GENERA LISTA CON LOS PUNTOS DE CADA JUGADOR TEMPORADA PASADA

testGraph3.insert(loc=0, column='team', value=teamList)                                            ## INSERTA LISTA CON LOS EQUIPOS DE CADA JUGADOR
testGraph3.insert(loc=1, column='position', value=positionList)                                    ## INSERTA LISTA CON LAS POSICIONES DE CADA JUGADOR
testGraph3['points last season'] = lastseasonpoints                                                ## INSERTA LISTA CON LOS PUNTOS DE CADA JUGADOR LA TEMPORADA PASADA
testGraph3['team'] = testGraph3['team'].replace([i for i in teams_df.id],[i for i in teams_df.name])                                            # REEMPLAZA CÓDIGO NUMÉRICO DE CADA EQUIPO POR EL NOMBRE REAL (EJ: ARSENAL = 1, ASTON VILLA = 2, etc)
testGraph3['position'] = testGraph3['position'].replace([i for i in elements_types_df.id],[i for i in elements_types_df.singular_name])         # REEMPLAZA CÓDIGO NUMÉRICO DE CADA POSICIÓN CON EL NOMBRE        

##MULTISELECT##
sorted_unique_team = sorted(testGraph3.team.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)             ## SELECCIONA TODOS LOS EQUIPOS EN ORDEN ALFABÉTICO

##MULTISELECT##
unique_pos = ['Goalkeeper','Defender','Midfielder','Forward']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)                          ## SELECCIONA TODOS LAS POSICIONES

df_selected_team = testGraph3[(testGraph3.team.isin(selected_team)) & (testGraph3.position.isin(selected_pos))]               ## CREO UN DATAFRAME QUE FILTRA TABLA CON RESPECTO AL INPUT EN LA PAGINA DE EQUIPOS Y POSICIONES QUE SE SELECCIONEN
final_df = df_selected_team.sort_values(by=['Total Points'], ascending=False)                                                 ## DATAFRAME FINAL, ENTREGA TABLA CON JUGADORES CON MAS PUNTAJE ARRIBA                                                                                                        

st.dataframe(final_df)                                                                             ## MUESTRA EL DATAFRAME FINAL EN LA PÁGINA


### DESCARGA EN CSV ###

def filedownload(df):                                                   
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerpoints.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(final_df), unsafe_allow_html=True)
