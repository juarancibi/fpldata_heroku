import requests
import pandas as pd
    
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
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

gwList = ['GW' + ' ' + str(i) for i in range(1,current_gw)]
        
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

testGraph = pd.DataFrame(data=pointsArray, index=nameList, columns=gwList)
testGraph.index.name = 'player name'
testGraph.insert(loc=0, column='id', value=idList)
testGraph.insert(loc=1, column='team', value=teamList)
testGraph.insert(loc=2, column='position', value=positionList)

testGraph['team'] = testGraph['team'].replace([i for i in teams_df.id],[i for i in teams_df.name])
testGraph['position'] = testGraph['position'].replace([i for i in elements_types_df.id],[i for i in elements_types_df.singular_name])

testGraph.to_csv('/Users/aranc/fpl/testGraph.csv')