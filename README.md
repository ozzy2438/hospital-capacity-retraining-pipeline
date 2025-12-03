# Hospital Capacity Retraining Pipeline

Automated ML retraining pipeline for hospital capacity surge prediction with drift detection, Airflow orchestration, and auto-promotion.

## Features

- **Monthly Scheduled Retraining**: Airflow DAG runs on the 1st of each month
- **Drift Detection**: KS test for feature distribution changes
- **Auto-Promotion**: Models promoted only if they meet performance criteria
- **Alerting**: Slack/email notifications on success/failure

## Auto-Promotion Criteria

- AUC ≥ 0.94
- No degradation > 0.02 from previous model
- Precision improvement required

## Setup

1. Configure Slack webhook in Airflow connections
2. Create `reference_data.npz` baseline for drift detection
3. Set email SMTP in Airflow config
4. Place training data in `train_data.npz` and validation in `val_data_2023.npz`

## Pipeline Flow

```
Drift Detection → Model Retraining → Evaluation → Auto-Promotion → Alerts
```

## Files

- `drift_detection.py`: Feature drift detection using KS test
- `retrain_model.py`: Model training and evaluation script
- `airflow_dags/monthly_retrain_dag.py`: Airflow orchestration

## Retraining Policy

**Schedule-based**: Monthly (1st of month)

**Performance triggers**:
- AUC drops below 0.85
- Accuracy drops >5%
- Precision/recall imbalance

**Data drift triggers**:
- New external data sources
- Distribution shifts
- Seasonal pattern changes

**Business triggers**:
- New product categories
- Operational changes
- Regulatory updates
