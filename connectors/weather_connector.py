import requests
import pandas as pd
from datetime import datetime, timedelta

class NOAAWeatherConnector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'
    
    def fetch_daily_weather(self, location_id, start_date, end_date):
        params = {
            'datasetid': 'GHCND',
            'locationid': location_id,
            'startdate': start_date,
            'enddate': end_date,
            'datatypeid': 'TMAX,TMIN,PRCP,AWND',
            'units': 'metric',
            'limit': 1000
        }
        headers = {'token': self.api_key}
        
        response = requests.get(self.base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()['results']
        df = pd.DataFrame(data)
        
        # Pivot to wide format
        df_pivot = df.pivot_table(
            index='date', 
            columns='datatype', 
            values='value', 
            aggfunc='first'
        ).reset_index()
        
        df_pivot.columns.name = None
        return df_pivot

# Usage:
# connector = NOAAWeatherConnector(api_key='YOUR_KEY_HERE')
# weather_df = connector.fetch_daily_weather('CITY:US370019', '2025-01-01', '2025-01-31')
