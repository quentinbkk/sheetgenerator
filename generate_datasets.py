# This the shape generator file for Excel spreadsheets
# Test Runs: Create 20 spreadsheets in long format (4 columns (Date, Channel, Metric, Value), 8 rows)
# Noise transformations: random values for int, set value of strings for now (Daily granularity for date, 2 choices for Channel and Metric)

import pandas as pd
import numpy as np
from itertools import product
import random
import os

def generate_synthetic_long(
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

def generate_multiindex_sheets(
    num_dates=2,
    add_empty_cells=True,
    empty_frac=0.1,
    change_types=True,
    wrong_type_cells=[('TV', 'Spend')]
):
    # Generate date range
    base_date = pd.to_datetime('2025-07-10') + pd.Timedelta(days=np.random.randint(0, 100))
    dates = pd.date_range(start=base_date, periods=num_dates, freq='7D')

    # Channels and metrics
    channels = ['TV', 'Radio']
    metrics = ['Spend', 'GRPs']

    # Build row-by-row dictionary
    records = []
    for date in dates:
        row = {}
        for ch in channels:
            for m in metrics:
                val = np.random.randint(50, 201) if m == 'Spend' else np.random.randint(1, 11)
                row[(ch, m)] = val
        row['Date'] = date
        records.append(row)

    # Create DataFrame
    df = pd.DataFrame(records)

    # Set Date as index, MultiIndex for columns
    df.set_index('Date', inplace=True)
    df.columns = pd.MultiIndex.from_tuples(df.columns)

    # Introduce NaNs
    if add_empty_cells:
        total_cells = df.size
        num_empty = int(total_cells * empty_frac)
        for _ in range(num_empty):
            row = np.random.choice(df.index)
            col = random.choice(df.columns)
            df.at[row, col] = np.nan

    # Introduce wrong types
    if change_types:
        for col in wrong_type_cells:
            if col in df.columns:
                for row in np.random.choice(df.index, size=max(1, len(df)//8), replace=False):
                    df.at[row, col] = random.choice(['low', 'NaN', 'unknown'])

    return df



# For multi table (Both these must be included)

def generate_multi_table(num_dates=2):
    base_date = pd.to_datetime('2025-07-10') + pd.Timedelta(days=np.random.randint(0, 100))
    dates = pd.date_range(base_date, periods=num_dates, freq='7D')

    rows = []
    for date in dates:
        for metric in ['Spend', 'GRPs']:
            tv_value = np.random.randint(50, 201) if metric == 'Spend' else np.random.randint(1, 11)
            radio_value = np.random.randint(50, 201) if metric == 'Spend' else np.random.randint(1, 11)
            rows.append([date.strftime('%d/%m/%Y'), metric, tv_value, radio_value])

    df = pd.DataFrame(rows, columns=['Date', 'Metric', 'TV', 'Radio'])
    return df

def generate_multitable_campaign_sheet(
    num_campaigns=3,
    num_dates=2,
    add_empty_cells=True,
    empty_frac=0.1,
    change_types=True
):
    tables = []
    for i in range(num_campaigns):
        df = generate_multi_table(num_dates)

        # Add empty cells
        if add_empty_cells:
            total_cells = df.size
            num_empty = int(total_cells * empty_frac)
            for _ in range(num_empty):
                row = np.random.randint(0, df.shape[0])
                col = np.random.choice(df.columns)
                df.at[row, col] = np.nan

        # Add wrong data types
        if change_types:
            for col in ['TV', 'Radio']:
                for row in np.random.choice(df.index, size=max(1, len(df)//6), replace=False):
                    df.at[row, col] = random.choice(['low', 'missing'])

        # Add campaign label to columns
        df.columns = pd.MultiIndex.from_product([[f'Campaign {chr(65 + i)}'], df.columns])
        tables.append(df)

        # Insert a visible spacer column after each campaign (except the last)
        if i < num_campaigns - 1:
            spacer = pd.DataFrame({'Spacer': [''] * df.shape[0]})
            spacer.columns = pd.MultiIndex.from_tuples([(' ', ' ')])  # visually blank header
            tables.append(spacer)

    return pd.concat(tables, axis=1)
    




    