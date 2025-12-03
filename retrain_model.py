import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from datetime import datetime
import os

# Load current production model
with open('capacity_surge_model_v2_2025.pkl', 'rb') as f:
    old_model = pickle.load(f)

# Load training data
train_data = np.load('train_data.npz')
X_train = train_data['X']
y_train = train_data['y']

# Load validation data
val_data = np.load('val_data_2023.npz')
X_val = val_data['X']
y_val = val_data['y']

# Train new model
print('Training new model...')
new_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1
)
new_model.fit(X_train, y_train)

# Evaluate both models
old_pred = old_model.predict_proba(X_val)[:, 1]
new_pred = new_model.predict_proba(X_val)[:, 1]

old_auc = roc_auc_score(y_val, old_pred)
new_auc = roc_auc_score(y_val, new_pred)

old_precision = precision_score(y_val, (old_pred > 0.5).astype(int))
new_precision = precision_score(y_val, (new_pred > 0.5).astype(int))

print('Old Model - AUC: ' + str(round(old_auc, 4)) + ', Precision: ' + str(round(old_precision, 4)))
print('New Model - AUC: ' + str(round(new_auc, 4)) + ', Precision: ' + str(round(new_precision, 4)))

# Auto-promotion criteria
PROMOTE = False
if new_auc >= 0.94 and new_auc >= old_auc - 0.02 and new_precision >= old_precision:
    PROMOTE = True
    timestamp = datetime.now().strftime('%Y%m%d')
    model_path = f'capacity_surge_model_v3_{timestamp}.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(new_model, f)
    print(f'Model promoted to production: {model_path}')
else:
    print('Model did not meet promotion criteria')
    print(f'Criteria: AUC >= 0.94 ({new_auc >= 0.94}), No degradation ({new_auc >= old_auc - 0.02}), Precision improvement ({new_precision >= old_precision})')
