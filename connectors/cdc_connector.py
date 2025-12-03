import requests
import pandas as pd

class CDCFluViewConnector:
    def __init__(self):
        self.base_url = 'https://data.cdc.gov/resource/g62h-syeh.json'
    
    def fetch_flu_data(self, start_week, end_week):
        params = {
            '$where': f"week >= '{start_week}' AND week <= '{end_week}'",
            '$limit': 10000
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        df = pd.DataFrame(response.json())
        
        # Select key columns
        cols = ['week', 'ilitotal', 'total_patients', 'percent_positive']
        df = df[[c for c in cols if c in df.columns]]
        
        return df

# Usage:
# connector = CDCFluViewConnector()
# flu_df = connector.fetch_flu_data('202501', '202504')
