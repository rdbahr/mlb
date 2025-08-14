from pybaseball import schedule_and_record
import datetime as dt
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import configparser

config = configparser.ConfigParser()
config.read('connect.ini')

es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    basic_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
)
#es.info()

year = '2024'
team = 'ARI'

team_rec = schedule_and_record(int(year), team)

team_rec['Date'] = team_rec['Date'].astype(str) + ' ' + year
team_rec['Date'] = team_rec['Date'].str.replace(r'\(\d\)\s', '', regex=True)
team_rec['Date'] = pd.to_datetime(team_rec['Date'], format='%A, %b %d %Y').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# Write to csv
#f_name = team + '_rec_' + year + '.csv'
#team_rec.to_csv(f_name, index=False)

# TO DO: Convert DataFrame to JSON docs

#es.index(
#    index='mlb_games',
#    document=es_doc_json
#)
