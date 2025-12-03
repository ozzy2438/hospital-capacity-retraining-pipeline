from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta
import subprocess

def run_retrain_script():
    result = subprocess.run(['python', 'retrain_model.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f'Retraining failed: {result.stderr}')
    return result.stdout

def check_drift():
    from drift_detection import check_feature_drift
    return check_feature_drift()

def send_failure_alert(context):
    return SlackWebhookOperator(
        task_id='slack_alert',
        http_conn_id='slack_webhook',
        message=f"Model retraining failed: {context['exception']}",
        channel='#ml-alerts'
    ).execute(context)

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email': ['ml-team@hospital.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': send_failure_alert
}

with DAG(
    'monthly_model_retrain',
    default_args=default_args,
    description='Monthly hospital capacity model retraining with drift detection',
    schedule_interval='0 0 1 * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['ml', 'retraining']
) as dag:
    
    drift_check = PythonOperator(
        task_id='detect_drift',
        python_callable=check_drift
    )
    
    retrain = PythonOperator(
        task_id='retrain_model',
        python_callable=run_retrain_script
    )
    
    success_alert = SlackWebhookOperator(
        task_id='success_notification',
        http_conn_id='slack_webhook',
        message='Model retraining completed successfully',
        channel='#ml-alerts'
    )
    
    drift_check >> retrain >> success_alert
