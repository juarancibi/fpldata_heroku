# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 18:26:28 2021

@author: aranc
"""


import streamlit as st
import pandas as pd
import requests

st.write('# Fantasy Premier League Data Exploration')

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json = r.json()
json.keys()
events_df = pd.DataFrame(json['events'])
elements_df = pd.DataFrame(json['elements'])
elements_df = elements_df[['id','web_name','team','element_type','selected_by_percent','now_cost','minutes',
                                'transfers_in','value_season','total_points','event_points']]
teams_df = pd.DataFrame(json['teams'])
elements_types_df = pd.DataFrame(json['element_types'])

teamList = list(elements_df.team)
positionList = list(elements_df.element_type)
eventpointsList = list(elements_df.event_points)
current_gw = events_df.id[events_df['is_current'] == True].tolist()[0]

url2 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/testGraph.csv?token=AQBPKDFZZNI623L46MN4WFLAQIQ3Y'
testGraph2 = pd.read_csv(url,index_col=0).set_index('player name')
testGraph2.drop(['id','team','position'], axis=1, inplace=True)
testGraph2['GW'+' '+str(current_gw)] = list(eventpointsList)

slider_1, slider_2 = st.slider("gameweeks", 1, current_gw,(1, current_gw))
testGraph3 = testGraph2.iloc[:, slider_1-1:slider_2]
testGraph3['Total Points'] =  testGraph3.sum(axis=1)

testGraph3.insert(loc=0, column='team', value=teamList)
testGraph3.insert(loc=1, column='position', value=positionList)
testGraph3['team'] = testGraph3['team'].replace([i for i in teams_df.id],[i for i in teams_df.name])
testGraph3['position'] = testGraph3['position'].replace([i for i in elements_types_df.id],[i for i in elements_types_df.singular_name])

sorted_unique_team = sorted(testGraph3.team.unique())
selected_team = st.multiselect('Team', sorted_unique_team, sorted_unique_team)

unique_pos = ['Goalkeeper','Defender','Midfielder','Forward']
selected_pos = st.multiselect('Position', unique_pos, unique_pos)

df_selected_team = testGraph3[(testGraph3.team.isin(selected_team)) & (testGraph3.position.isin(selected_pos))]
final_df = df_selected_team.sort_values(by=['Total Points'], ascending=False)

st.dataframe(final_df)
