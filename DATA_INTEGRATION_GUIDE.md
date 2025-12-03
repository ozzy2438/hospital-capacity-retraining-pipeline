# Data Source Integration Guide

## 1. External Data Sources - Access & APIs

### Weather Data (NOAA)
**API**: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
**Access**: Free API key at https://www.ncdc.noaa.gov/cdo-web/token
**Endpoint**: `/data?datasetid=GHCND&locationid=CITY:US370019&startdate=2025-01-01`
**Key Features**: temperature, precipitation, humidity
**Join Key**: `date` + `hospital_location`

### CDC FluView
**API**: https://data.cdc.gov/resource/g62h-syeh.json
**Access**: Public, no auth required
**Endpoint**: `https://data.cdc.gov/resource/g62h-syeh.json?week=202501`
**Key Features**: ILI percentage, total patients
**Join Key**: `week` (ISO week number)

### Google Trends (pytrends)
**Library**: `pip install pytrends`
**Access**: No API key needed
**Code**: `pytrends.interest_over_time(['flu symptoms'])`
**Key Features**: search volume index
**Join Key**: `date`

### Census/Socioeconomic (census.gov)
**API**: https://api.census.gov/data.html
**Access**: Free API key at https://api.census.gov/data/key_signup.html
**Endpoint**: `/data/2021/acs/acs5?get=B01001_001E&for=county:*`
**Key Features**: population, income, unemployment
**Join Key**: `county_fips` or `zip_code`

## 2. Internal Data Sources

### EMS Dispatch Logs
**Source**: Hospital CAD system or county 911 dispatch
**Access**: Internal database or file export
**Format**: CSV/JSON from dispatch software
**Key Features**: call volume, response times, call types
**Join Key**: `timestamp` + `destination_hospital`

### Staff Scheduling
**Source**: Kronos/WorkDay/internal HR system
**Access**: Database view or API
**Format**: Scheduled shifts by department
**Key Features**: nurse_count, doctor_count, shift_coverage
**Join Key**: `date` + `shift` + `department`

### Bed Management System
**Source**: Epic/Cerner bed tracking module
**Access**: HL7 feed or database view
**Format**: Real-time bed status
**Key Features**: available_beds, occupied_beds, pending_discharges
**Join Key**: `timestamp` + `unit`

## 3. Data Pipeline Architecture

```
External APIs → Landing Zone (S3/GCS) → ETL (Airflow) → Feature Store → Model Training
Internal DBs → Change Data Capture → Staging Tables → Feature Engineering → Inference
```

## 4. Feature Join Strategy

### Base Table: `hospital_admissions`
- admission_id (PK)
- admission_datetime
- hospital_id
- patient_zip
- department

### Join Pattern:
```sql
SELECT 
    a.*,
    w.temperature, w.humidity,
    f.ili_percentage,
    t.search_volume,
    s.nurse_count,
    b.available_beds
FROM hospital_admissions a
LEFT JOIN weather_daily w 
    ON DATE(a.admission_datetime) = w.date 
    AND a.hospital_id = w.location_id
LEFT JOIN cdc_fluview f 
    ON YEARWEEK(a.admission_datetime) = f.week
LEFT JOIN google_trends t 
    ON DATE(a.admission_datetime) = t.date
LEFT JOIN staff_schedule s 
    ON DATE(a.admission_datetime) = s.date 
    AND a.department = s.department
LEFT JOIN bed_status b 
    ON a.admission_datetime BETWEEN b.snapshot_time - INTERVAL 1 HOUR 
    AND b.snapshot_time
```

## 5. Implementation Steps

### Phase 1: Quick Wins (Week 1)
1. Set up NOAA weather API connector
2. Install pytrends for Google Trends
3. Create Airflow DAG for daily weather ingestion
4. Add weather features to training data

### Phase 2: Internal Integration (Week 2-3)
1. Get database credentials for EMS/scheduling systems
2. Set up read-only views or API access
3. Build CDC data connector
4. Implement feature join logic

### Phase 3: Production (Week 4)
1. Schedule all data pipelines in Airflow
2. Add data quality checks
3. Update drift detection for new features
4. Retrain model with expanded feature set

## 6. Code Templates

### Weather API Connector
```python
import requests
import pandas as pd

def fetch_noaa_weather(start_date, end_date, location_id, api_key):
    url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'
    params = {
        'datasetid': 'GHCND',
        'locationid': location_id,
        'startdate': start_date,
        'enddate': end_date,
        'datatypeid': 'TMAX,TMIN,PRCP',
        'limit': 1000
    }
    headers = {'token': api_key}
    response = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(response.json()['results'])
```

### Google Trends Connector
```python
from pytrends.request import TrendReq

def fetch_google_trends(keywords, timeframe='today 3-m'):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords, timeframe=timeframe)
    return pytrends.interest_over_time()
```

### Feature Engineering Pipeline
```python
def engineer_features(df):
    # Temporal features
    df['day_of_week'] = df['admission_datetime'].dt.dayofweek
    df['hour'] = df['admission_datetime'].dt.hour
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Weather interactions
    df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
    
    # Lagged features
    df['beds_available_lag1'] = df.groupby('hospital_id')['available_beds'].shift(1)
    
    # Rolling aggregates
    df['admissions_7day_avg'] = df.groupby('hospital_id')['admission_id'].transform(
        lambda x: x.rolling(7, min_periods=1).count()
    )
    
    return df
```

## 7. Data Governance

### Access Requirements
- **External APIs**: Document API keys in secrets manager (AWS Secrets/Vault)
- **Internal DBs**: Request read-only service accounts
- **PII Handling**: Anonymize patient data, use zip code aggregation

### Monitoring
- Track API rate limits and failures
- Alert on missing data (>24hr gap)
- Monitor feature drift for new sources
- Log all data pulls for audit

## 8. Cost Estimates

| Source | Cost | Rate Limit |
|--------|------|------------|
| NOAA Weather | Free | 1000 requests/day |
| CDC FluView | Free | No limit |
| Google Trends | Free | ~100 requests/hour |
| Census API | Free | 500 requests/day |
| Internal DBs | Infrastructure only | N/A |

**Total External Cost**: $0/month
