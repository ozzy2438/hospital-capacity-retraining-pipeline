from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/dags')

from weather_connector import NOAAWeatherConnector
from trends_connector import GoogleTrendsConnector
from cdc_connector import CDCFluViewConnector

def fetch_weather_data(**context):
    connector = NOAAWeatherConnector(api_key='{{ var.value.noaa_api_key }}')
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    df = connector.fetch_daily_weather('CITY:US370019', start_date, end_date)
    df.to_csv('/opt/airflow/data/weather_latest.csv', index=False)
    return len(df)

def fetch_trends_data(**context):
    connector = GoogleTrendsConnector()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    df = connector.fetch_health_trends(['flu symptoms', 'covid symptoms'], start_date, end_date)
    df.to_csv('/opt/airflow/data/trends_latest.csv', index=False)
    return len(df)

def fetch_flu_data(**context):
    connector = CDCFluViewConnector()
    current_week = datetime.now().strftime('%Y%W')
    start_week = (datetime.now() - timedelta(weeks=4)).strftime('%Y%W')
    
    df = connector.fetch_flu_data(start_week, current_week)
    df.to_csv('/opt/airflow/data/flu_latest.csv', index=False)
    return len(df)

default_args = {
    'owner': 'ml-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'daily_external_data_ingestion',
    default_args=default_args,
    description='Fetch external data sources daily',
    schedule_interval='0 2 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False
) as dag:
    
    weather_task = PythonOperator(
        task_id='fetch_weather',
        python_callable=fetch_weather_data
    )
    
    trends_task = PythonOperator(
        task_id='fetch_trends',
        python_callable=fetch_trends_data
    )
    
    flu_task = PythonOperator(
        task_id='fetch_flu',
        python_callable=fetch_flu_data
    )
    
    [weather_task, trends_task, flu_task]
