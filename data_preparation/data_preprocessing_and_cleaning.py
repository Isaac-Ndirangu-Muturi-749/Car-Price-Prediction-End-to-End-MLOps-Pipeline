#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os

# Define the path to the data directory
data_dir = '../data'

# List all CSV files in the directory
csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

# Define a function to standardize column names
def standardize_columns(df):
    df.columns = [col.lower().replace(' ', '_').replace('£', '') for col in df.columns]
    return df

# Load, standardize, and inspect each dataset
dataframes = {}
for file in csv_files:
    file_path = os.path.join(data_dir, file)
    df = pd.read_csv(file_path)
    df = standardize_columns(df)
    dataframes[file] = df
    print(f"--- {file} ---")
    print(df.head())
    print("\n")


# Define a function to clean data
def clean_data(df):
    # Drop rows with missing values
    df = df.dropna()

    # Convert year and price to numeric
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['price'] = df['price'].replace('[£,]', '', regex=True).astype(float)

    # Convert tax to numeric if exists
    if 'tax' in df.columns:
        df['tax'] = df['tax'].replace('[£,]', '', regex=True).astype(float)
    if 'tax_' in df.columns:
        df['tax_'] = df['tax_'].replace('[£,]', '', regex=True).astype(float)

    return df

# Clean each dataset
for file, df in dataframes.items():
    dataframes[file] = clean_data(df)
    print(f"--- {file} ---")
    print(df.head())
    print("\n")

# Combine datasets
combined_df = pd.concat(dataframes.values(), ignore_index=True)

# Save the combined dataset
combined_df.to_csv('../data/combined_car_data.csv', index=False)
print("Combined dataset saved to 'combined_car_data.csv'.")


# # Clean Up Redundant Columns:
columns_to_drop = ['tax()', 'fuel_type', 'engine_size', 'mileage2', 'fuel_type2', 'engine_size2', 'reference']
combined_df = combined_df.drop(columns=columns_to_drop)

# Create a mapping dictionary to combine unclean categories
make_mapping = {
    'unclean focus': 'focus',
    'unclean cclass': 'cclass'
}

# Apply the mapping to the 'make' column
combined_df['make'] = combined_df['make'].replace(make_mapping)

# # Convert mileage to Numeric:
combined_df['mileage'] = combined_df['mileage'].replace('[\D]', '', regex=True).astype(float)

# # Handle Missing Values:
combined_df['fueltype'] = combined_df['fueltype'].fillna(combined_df['fueltype'].mode()[0])
combined_df['enginesize'] = combined_df['enginesize'].fillna(combined_df['enginesize'].median())
combined_df['tax'] = combined_df['tax'].fillna(combined_df['tax'].median())
combined_df['mpg'] = combined_df['mpg'].fillna(combined_df['mpg'].median())

# # Feature Engineering:
combined_df = pd.get_dummies(combined_df, columns=['make', 'transmission', 'fueltype'], drop_first=True)

# # Handle Unusual Year Values:
combined_df = combined_df[combined_df['year'].between(1980, 2024)]  # Adjust the range as necessary

# Handle Outliers in Price:
from scipy import stats
z_scores = np.abs(stats.zscore(combined_df['price'].dropna()))
filtered_df = combined_df[(z_scores < 3)]

# Cap extreme values for mileage
combined_df = combined_df[combined_df['mileage'].astype(float) <= 200000]

# Cap extreme values for mpg
combined_df = combined_df[combined_df['mpg'] <= 100]

# drop duplicate rows
combined_df = combined_df.drop_duplicates()

# # Handle Low-Frequency Categories:
# Drop columns with low-frequency categories
combined_df_cleaned = combined_df.drop(columns=['transmission_Other', 'fueltype_Electric', 'fueltype_Other', 'model'])

# Save the cleaned DataFrame to a CSV file
combined_df_cleaned.to_csv('../data/cleaned_car_data.csv', index=False)
