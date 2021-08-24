# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 11:31:17 2021

@author: aranc
"""

import streamlit as st
import pandas as pd
import base64
import requests

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



st.sidebar.header('Filters')
selected_year = st.sidebar.selectbox('Year', [2020,2021])

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
url2 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/pointsbygw.csv'           ## URL DEL ARCHIVO EN GITHUB, TABLA DEL 2020 CREADA POR OTRO ARCHIVO PYTHON

r = requests.get(url)
json = r.json()
json.keys()
elements_df = pd.DataFrame(json['elements'])
elements_df = elements_df[['id','web_name','team','element_type','selected_by_percent','now_cost','minutes',
                                        'transfers_in','value_season','total_points','event_points']]
elements_types_df = pd.DataFrame(json['element_types'])
teams_df = pd.DataFrame(json['teams'])
events_df = pd.DataFrame(json['events'])
    
idList = list(elements_df.id)
nameList = list(elements_df.web_name)
teamList = list(elements_df.team)
positionList = list(elements_df.element_type)

current_gw = events_df.id[events_df['is_current'] == True].tolist()[0]

@st.cache
def load_data(year):
    
    if year == 2020:
        playerpoints = pd.read_csv(url2,index_col=0)
        playerpoints.drop(['id','team','position'], axis=1, inplace=True)
    else:
        gwList = ['GW' + ' ' + str(i) for i in range(1,current_gw + 1)]
        pointsArray = []
        for x in elements_df.index:
            element_id = elements_df.id[x]
            url = f'https://fantasy.premierleague.com/api/element-summary/{element_id}/'
            r = requests.get(url)
            json = r.json()
            json_history_df = pd.DataFrame(json['history'])
            json_history_df = json_history_df.groupby(['round'], as_index=False)['total_points'].sum()
            json_history_df.set_index("round")
            new_index = pd.Index(range(1,current_gw+1), name="round")
            json_history_df = json_history_df.set_index("round").reindex(new_index)
            points = list(json_history_df.total_points)
            pointsArray.append(points)      
        playerpoints = pd.DataFrame(data=pointsArray, index=nameList, columns=gwList)
    return playerpoints

playerpoints = load_data(selected_year)

if selected_year == 2020:
    slider_1, slider_2 = st.sidebar.slider("Gameweek", 1, 38,(1, 38))                  ## SELECCIONA TODOS LOS GAMEWEEKS ACTUALES POR DEFECTO
    playerpoints = playerpoints.iloc[:, slider_1-1:slider_2]                                               ## GENERA DATAFRAME CON LOS GAMEWEEKS SELECCIONADOS EN LA PÁGINA
    playerpoints['Total Points'] =  playerpoints.sum(axis=1)          
    playerpoints.insert(loc=0, column='team', value=list(pd.read_csv(url2,index_col=0).team))
    playerpoints.insert(loc=1, column='position', value=list(pd.read_csv(url2,index_col=0).position)) 
else:
    slider_1, slider_2 = st.sidebar.slider("Gameweek", 1, current_gw,(1, current_gw))                  ## SELECCIONA TODOS LOS GAMEWEEKS ACTUALES POR DEFECTO
    playerpoints = playerpoints.iloc[:, slider_1-1:slider_2]                                               ## GENERA DATAFRAME CON LOS GAMEWEEKS SELECCIONADOS EN LA PÁGINA
    playerpoints['Total Points'] =  playerpoints.sum(axis=1)          
    playerpoints.insert(loc=0, column='team', value=teamList)                                            ## INSERTA LISTA CON LOS EQUIPOS DE CADA JUGADOR
    playerpoints.insert(loc=1, column='position', value=positionList)                                    ## INSERTA LISTA CON LAS POSICIONES DE CADA JUGADOR
    playerpoints['team'] = playerpoints['team'].replace([i for i in teams_df.id],[i for i in teams_df.name])                                            # REEMPLAZA CÓDIGO NUMÉRICO DE CADA EQUIPO POR EL NOMBRE REAL (EJ: ARSENAL = 1, ASTON VILLA = 2, etc)
    playerpoints['position'] = playerpoints['position'].replace([i for i in elements_types_df.id],[i for i in elements_types_df.singular_name])         # REEMPLAZA CÓDIGO NUMÉRICO DE CADA POSICIÓN CON EL NOMBRE        

sorted_unique_team = sorted(playerpoints.team.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

unique_pos = ['Goalkeeper','Defender','Midfielder','Forward']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)  

df_selected_team = playerpoints[(playerpoints.team.isin(selected_team)) & (playerpoints.position.isin(selected_pos))]               ## CREO UN DATAFRAME QUE FILTRA TABLA CON RESPECTO AL INPUT EN LA PAGINA DE EQUIPOS Y POSICIONES QUE SE SELECCIONEN
playerpoints = df_selected_team.sort_values(by=['Total Points'], ascending=False)   

st.write('Data Dimension: ' + str(playerpoints.shape[0]) + ' rows and ' + str(playerpoints.shape[1]) + ' columns.')
st.dataframe(playerpoints)

def filedownload(df):                                                   
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerpoints.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(playerpoints), unsafe_allow_html=True)
