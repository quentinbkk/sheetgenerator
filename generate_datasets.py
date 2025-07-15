# This the shape generator file for Excel spreadsheets
# Test Runs: Create 20 spreadsheets in long format (4 columns (Date, Channel, Metric, Value), 8 rows)
# Noise transformations: random values for int, set value of strings for now (Daily granularity for date, 2 choices for Channel and Metric)

import pandas as pd
import numpy as np
from itertools import product
import random
import os


output_folder = 'long_first'

def generate_synthetic_df(
    num_rows=16,
    add_empty_cells=True,
    empty_frac=0.1,
    change_types=True,
    wrong_type_cols=['Value']
):
    # Generate date range
    base_date = pd.to_datetime('2025-07-10') + pd.Timedelta(days=np.random.randint(0, 365))
    dates = pd.date_range(base_date, periods=num_rows//4, freq='7D')

    # Generate combinations
    channels = ['TV', 'Radio']
    metrics = ['Spend', 'GRPs']
    all_combinations = list(product(dates, channels, metrics))
    df = pd.DataFrame(all_combinations, columns=['Date', 'Channel', 'Metric'])

    # Assign values
    def random_value(metric):
        if metric == 'Spend':
            return np.random.randint(50, 201)
        return np.random.randint(1, 11)

    df['Value'] = df['Metric'].apply(random_value)

    # Pad or trim to desired num_rows
    if len(df) < num_rows:
        df = pd.concat([df] * (num_rows // len(df) + 1), ignore_index=True)
    df = df.sample(n=num_rows, random_state=42).reset_index(drop=True)

    # Introduce empty cells
    if add_empty_cells:
        total_cells = df.size
        num_empty = int(total_cells * empty_frac)
        for _ in range(num_empty):
            row = np.random.randint(0, df.shape[0])
            col = np.random.choice(df.columns)
            df.at[row, col] = np.nan

    # Introduce wrong data types
    if change_types:
        for col in wrong_type_cols:
            for row in np.random.choice(df.index, size=max(1, len(df)//8), replace=False):
                if col == 'Value':
                    df.at[row, col] = random.choice(['one hundred', 'ten', 'NaN'])
                elif col == 'Date':
                    df.at[row, col] = random.choice(['not a date', 'yesterday', 'soon'])

    return df

os.makedirs(output_folder, exist_ok=True)

NUM_SETS = 20

for i in range(NUM_SETS):
    params = {
        'num_rows': random.randint(12, 50),
        'add_empty_cells': random.choice([True, False]),
        'empty_frac': round(random.uniform(0.05, 0.3), 2),
        'change_types': random.choice([True, False]),
        'wrong_type_cols': random.sample(['Value', 'Date'], 
                                         k=random.randint(0, 2))
    }

    df = generate_synthetic_df(**params)
    filepath = os.path.join(output_folder, f'synthetic_dataset_{i+1}.xlsx')
    df.to_excel(filepath, index=False)

    print(f"Saved: {filepath}")