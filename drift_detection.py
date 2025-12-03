import numpy as np
from scipy import stats
import json

def detect_drift(reference_data, current_data, threshold=0.05):
    """
    Detect feature drift using Kolmogorov-Smirnov test
    Returns dict with drift status per feature
    """
    drift_report = {}
    
    for i in range(reference_data.shape[1]):
        ref_feature = reference_data[:, i]
        curr_feature = current_data[:, i]
        
        # KS test
        statistic, p_value = stats.ks_2samp(ref_feature, curr_feature)
        
        drift_report[f'feature_{i}'] = {
            'drift_detected': p_value < threshold,
            'p_value': float(p_value),
            'ks_statistic': float(statistic)
        }
    
    return drift_report

def check_feature_drift():
    # Load reference and current data
    reference = np.load('reference_data.npz')['X']
    current = np.load('train_data.npz')['X']
    
    drift_report = detect_drift(reference, current)
    
    # Save report
    with open('drift_report.json', 'w') as f:
        json.dump(drift_report, f, indent=2)
    
    # Check if any drift detected
    drift_count = sum(1 for v in drift_report.values() if v['drift_detected'])
    
    if drift_count > 0:
        print(f'WARNING: Drift detected in {drift_count} features')
    else:
        print('No significant drift detected')
    
    return drift_report
