"""Debug script to check conf_int structure."""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from src.data_loader import DataLoader

# Load data
loader = DataLoader()
df = loader.load_data('MMM dataset - Sheet1.csv')

# Prepare simple model
channels = ['tv_spend', 'radio_spend']
X = df[channels].values
y = df['new_customers'].values

# Add constant
X_sm = sm.add_constant(X)

# Fit model
model = sm.OLS(y, X_sm).fit()

print("Model params:")
print(model.params)
print(f"Type: {type(model.params)}")
print()

print("Model bse:")
print(model.bse)
print(f"Type: {type(model.bse)}")
print()

print("Model conf_int():")
conf_int = model.conf_int()
print(conf_int)
print(f"Type: {type(conf_int)}")
print(f"Shape: {conf_int.shape}")
print()

print("conf_int[0]:")
print(conf_int[0])
print(f"Type: {type(conf_int[0])}")
print()

print("conf_int[1]:")
print(conf_int[1])
print(f"Type: {type(conf_int[1])}")
print()

print("Accessing by column index:")
print("conf_int.iloc[:, 0]:")
print(conf_int.iloc[:, 0])
print()

print("conf_int.iloc[:, 1]:")
print(conf_int.iloc[:, 1])
