import pandas as pd

def join_external_features(admissions_df, weather_df, trends_df, flu_df):
    # Ensure date columns are datetime
    admissions_df['date'] = pd.to_datetime(admissions_df['admission_datetime']).dt.date
    weather_df['date'] = pd.to_datetime(weather_df['date']).dt.date
    trends_df['date'] = pd.to_datetime(trends_df['date']).dt.date
    
    # Create week column for flu data join
    admissions_df['week'] = pd.to_datetime(admissions_df['admission_datetime']).dt.strftime('%Y%W')
    
    # Join weather data
    df = admissions_df.merge(
        weather_df,
        on='date',
        how='left'
    )
    
    # Join trends data
    df = df.merge(
        trends_df,
        on='date',
        how='left'
    )
    
    # Join flu data
    df = df.merge(
        flu_df,
        on='week',
        how='left'
    )
    
    # Fill missing values with forward fill then backward fill
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
    
    return df

# Usage:
# enriched_df = join_external_features(admissions, weather, trends, flu)
