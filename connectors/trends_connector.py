from pytrends.request import TrendReq
import pandas as pd

class GoogleTrendsConnector:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    def fetch_health_trends(self, keywords, start_date, end_date):
        timeframe = start_date + ' ' + end_date
        self.pytrends.build_payload(keywords, timeframe=timeframe)
        df = self.pytrends.interest_over_time()
        
        if not df.empty:
            df = df.drop('isPartial', axis=1)
            df = df.reset_index()
            df.columns = ['date'] + [f'trend_{k.replace(" ", "_")}' for k in keywords]
        
        return df

# Usage:
# connector = GoogleTrendsConnector()
# trends_df = connector.fetch_health_trends(['flu symptoms', 'covid symptoms'], '2025-01-01', '2025-01-31')
