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

st.write("""
# Fantasy Premier League Data Exploration
         
Check players' points in each gameweek, using the FantasyPL API.
More info about the [game](https://fantasy.premierleague.com/)

         """)
         
st.markdown("""
            
* **Python libraries:** pandas, streamlit, base64
* **Data sources: ** endpoints are [bootstrap-static](https://fantasy.premierleague.com/api/bootstrap-static/),
                    [element-id (each player has an id)](https://fantasy.premierleague.com/api/element-summary/{element_id}/)
* **Github: ** [Github repository](https://github.com/juarancibi/fpldata_heroku)
            """)

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

st.write('The current gameweek is Gameweek ' + str(current_gw))

url2 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/testGraph.csv'
testGraph2 = pd.read_csv(url2,index_col=0)
testGraph2.drop(['id','team','position'], axis=1, inplace=True)
testGraph2['GW'+' '+str(current_gw)] = list(eventpointsList)

slider_1, slider_2 = st.sidebar.slider("Gameweek", 1, current_gw,(1, current_gw))
testGraph3 = testGraph2.iloc[:, slider_1-1:slider_2]
testGraph3['Total Points'] =  testGraph3.sum(axis=1)

url3 = 'https://raw.githubusercontent.com/juarancibi/fpldata_heroku/main/lastseason.csv'
lstseasongraph = pd.read_csv(url3, index_col=0)
lastseasonpoints = list(lstseasongraph.iloc[:,0])

testGraph3.insert(loc=0, column='team', value=teamList)
testGraph3.insert(loc=1, column='position', value=positionList)
testGraph3.insert(loc=2, column='points_last_season', value=lastseasonpoints)
testGraph3['team'] = testGraph3['team'].replace([i for i in teams_df.id],[i for i in teams_df.name])
testGraph3['position'] = testGraph3['position'].replace([i for i in elements_types_df.id],[i for i in elements_types_df.singular_name])

sorted_unique_team = sorted(testGraph3.team.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

unique_pos = ['Goalkeeper','Defender','Midfielder','Forward']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

df_selected_team = testGraph3[(testGraph3.team.isin(selected_team)) & (testGraph3.position.isin(selected_pos))]
final_df = df_selected_team.sort_values(by=['Total Points'], ascending=False)

st.dataframe(final_df)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerpoints.csv">Download CSV File</a>'
    return href

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="playerpoints.xlsx">Download Excel File</a>' # decode b'abc' => abc

st.markdown(filedownload(final_df), unsafe_allow_html=True)
