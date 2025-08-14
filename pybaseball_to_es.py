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
ari_rec = schedule_and_record(int(year), 'ARI')

ari_rec['Date'] = ari_rec['Date'].astype(str) + ' ' + year
ari_rec['Date'] = ari_rec['Date'].str.replace(r'\(\d\)\s', '', regex=True)
ari_rec['Date'] = pd.to_datetime(ari_rec['Date'], format='%A, %b %d %Y').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

#f_name = 'ari_rec_' + year + '.csv'
#ari_rec.to_csv(f_name, index=False)

# TO DO: Convert DataFrame to JSON docs
