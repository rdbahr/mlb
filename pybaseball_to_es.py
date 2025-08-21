from pybaseball import schedule_and_record
import datetime as dt
import pandas as pd
import sys
import re
import os
from elasticsearch import Elasticsearch, helpers
import configparser
import json

config = configparser.ConfigParser()
config.read('connect.ini')

# CLOUD
#es = Elasticsearch(
#    cloud_id=config['ELASTIC']['cloud_id'],
#    basic_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
#)

# ON-PREM
es = Elasticsearch(
    config['ELASTIC']['ES_HOST'],
    api_key=config['ELASTIC']['API_KEY']
)

# Test connection
#es.info()

# Load Component Template
with open('mlb_games_component_template.json') as f:
    mlb_g_ct = json.load(f)

with open(mlb_games_index_template.json) as g:
    mlb_g_it = json.load(g)

es.cluster.put_component_template(name="mlb_games", body=mlb_g_ct)
es.cluster.put_index_template(name="mlb_games" body=mlb_g_it)

ALE = pd.DataFrame({ 'Team': ['BAL', 'BOS', 'NYY', 'TBR', 'TOR'], 'League': 'AL', 'Division': 'ALE' })
ALC = pd.DataFrame({ 'Team': ['CLE', 'CHW', 'DET', 'KCR', 'MIN'], 'League': 'AL', 'Division': 'ALC' })
ALW = pd.DataFrame({ 'Team': ['OAK', 'HOU', 'LAA', 'SEA', 'TEX'], 'League': 'AL', 'Division': 'ALW' })
NLE = pd.DataFrame({ 'Team': ['ATL', 'MIA', 'NYM', 'PHI', 'WSN'], 'League': 'NL', 'Division': 'NLE' })
NLC = pd.DataFrame({ 'Team': ['CHC', 'CIN', 'MIL', 'PIT', 'STL'], 'League': 'NL', 'Division': 'NLC' })
NLW = pd.DataFrame({ 'Team': ['ARI', 'COL', 'LAD', 'SDP', 'SFG'], 'League': 'NL', 'Division': 'NLW' })

ALL = pd.concat([ALE, ALC, ALW, NLE, NLC, NLW], ignore_index=True)
ALLOpp = ALL.rename(columns={'Team': 'Opponent', 'League': 'OpponentLeague', 'Division': 'OpponentDivision'})

if re.match("\d{4}", sys.argv[1]):
  year = sys.argv[1]
else:
  year = '2024'
  print("Year not passed or invalid, using " + year + '.')

if sys.argv[2] == 'ALL':
  team_list = ALL
elif int(ALL['Team'].str.contains(sys.argv[2]).value_counts().get(True)) == 1:
  team_list = ALL[ALL['Team'].str.contains(sys.argv[2])]

rename_cols = {
  'Tm': 'Team', 'Opp': 'Opponent', 'W/L': 'WinLoss', 'R': 'Runs', 'RA': 'RunsAllowed',
  'Inn': 'Innings', 'GB': 'GamesBack', 'Win': 'PitcherWin', 'Loss': 'PitcherLoss',
  'Save': 'PitcherSave', 'Time': 'Duration', 'D/N': 'DayNight', 'cLI': 'ChampionshipLeverageIndex'
}

for index, row in team_list.iterrows():
  team = row['Team']
  print(team)
  team_rec = schedule_and_record(int(year), team)
  team_rec.rename(columns=rename_cols, inplace=True)
  # add league and division columns to team_rec
  team_rec = pd.merge(team_rec, ALL, on='Team', how='left')
  team_rec = pd.merge(team_rec, ALLOpp, on='Opponent', how='left')
  team_rec['Date'] = team_rec['Date'].astype(str) + ' ' + year
  team_rec['Date'] = team_rec['Date'].str.replace(r'\(\d\)\s', '', regex=True)
  team_rec['Date'] = pd.to_datetime(team_rec['Date'], format='%A, %b %d %Y').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
  team_rec['GamesBack'] = team_rec['GamesBack'].str.replace('Tied', '0.0')
  team_rec['GamesBack'] = team_rec['GamesBack'].str.replace(r'up\s?', '-', regex=True)
  team_rec['ChampionshipLeverageIndex'] = team_rec['ChampionshipLeverageIndex'].str.replace(r'(-+|\++)', '', regex=True)
  f_name = team + '_rec_' + year + '.csv'
  team_rec.to_csv(os.path.join('results', f_name), index=False)
  for index_rec, row_rec in team_rec.iterrows():
    row_rec_json = row_rec.to_json()
    es.index(
      index='mlb_games',
      document=row_rec_json
    )
