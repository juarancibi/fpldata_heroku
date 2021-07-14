# -*- coding: utf-8 -*-
"""
Created on Sat May  1 22:31:32 2021

@author: aranc
"""

import pandas as pd
import requests

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json = r.json()
json.keys()
elements_df = pd.DataFrame(json['elements'])
nameList = list(elements_df.web_name)

lastseasonpoints = []
for x in elements_df.index:
    element_id = elements_df.id[x]
    url = f'https://fantasy.premierleague.com/api/element-summary/{element_id}/'
    r = requests.get(url)
    json = r.json()
    json_history_past_df = pd.DataFrame(json['history_past'])
    lspoints = []
    if len(json_history_past_df) > 0:
        if json_history_past_df['season_name'][len(json_history_past_df)-1] == '2019/20' :
            lspoints = json_history_past_df.total_points[json_history_past_df['season_name'] == '2019/20'].tolist()[0]
        else:
            lspoints = float("nan")
    else:
        lspoints = float("nan")
    lastseasonpoints.append(lspoints)

lastseasongraph = pd.DataFrame(data=lastseasonpoints, index=nameList)
lastseasongraph.index.name = 'player name'
lastseasongraph.to_csv('/Users/aranc/fpl/lastseason.csv')