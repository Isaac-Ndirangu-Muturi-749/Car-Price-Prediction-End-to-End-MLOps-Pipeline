import os
import pandas as pd

def standardize_columns(df):
    """Standardize column names to lowercase and replace spaces with underscores."""
    df.columns = [col.lower().replace(' ', '_').replace('£', '') for col in df.columns]
    return df

def extract_make(filename):
    """Extract make from the filename."""
    return filename.split('.')[0]  # Assuming filename format is make.csv

def clean_data(df):
    """Clean the dataframe by handling missing values and converting data types."""
    df = df.dropna()  # Drop rows with missing values

    # Convert 'year' and 'price' to numeric
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['price'] = df['price'].replace('[£,]', '', regex=True).astype(float)

    # Convert 'tax' to numeric if exists
    if 'tax' in df.columns:
        df['tax'] = df['tax'].replace('[£,]', '', regex=True).astype(float)
    if 'tax_' in df.columns:
        df['tax_'] = df['tax_'].replace('[£,]', '', regex=True).astype(float)

    return df

def load_and_preprocess_data(data_dir):
    """Load and preprocess all CSV files in the given directory."""
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    dataframes = {}

    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        df = standardize_columns(df)
        df['make'] = extract_make(file)
        df = clean_data(df)
        columns = ['make'] + [col for col in df.columns if col != 'make']
        df = df[columns]
        dataframes[file] = df
        print(f"Processed {file}")

    combined_df = pd.concat(dataframes.values(), ignore_index=True)
    return combined_df

def main():
    data_dir = '../data/original/'
    output_file = '../data/cleaned_car_data.csv'

    combined_df = load_and_preprocess_data(data_dir)

    # Additional cleaning steps
    columns_to_drop = ['tax()', 'fuel_type', 'engine_size', 'mileage2', 'fuel_type2', 'engine_size2', 'reference']
    combined_df = combined_df.drop(columns=columns_to_drop, errors='ignore')

    # Replace unclean categories
    make_mapping = {'unclean focus': 'focus', 'unclean cclass': 'cclass'}
    combined_df['make'] = combined_df['make'].replace(make_mapping)
    combined_df['mileage'] = combined_df['mileage'].replace('[\D]', '', regex=True).astype(float)
    combined_df['fueltype'] = combined_df['fueltype'].fillna(combined_df['fueltype'].mode()[0])
    combined_df['enginesize'] = combined_df['enginesize'].fillna(combined_df['enginesize'].median())
    combined_df['tax'] = combined_df['tax'].fillna(combined_df['tax'].median())
    combined_df['mpg'] = combined_df['mpg'].fillna(combined_df['mpg'].median())

    # One-hot encode categorical columns
    combined_df = pd.get_dummies(combined_df, columns=['make', 'transmission', 'fueltype'], drop_first=True)

    # Filter extreme values
    combined_df = combined_df[combined_df['year'].between(1980, 2024)]
    combined_df = combined_df[combined_df['mileage'] <= 200000]
    combined_df = combined_df[combined_df['mpg'] <= 100]

    # Drop duplicates
    combined_df = combined_df.drop_duplicates()

    # Drop columns with low-frequency categories
    combined_df = combined_df.drop(columns=['transmission_Other', 'fueltype_Electric', 'fueltype_Other', 'model'], errors='ignore')

    # Save the cleaned dataset
    combined_df.to_csv(output_file, index=False)
    print(f"Cleaned dataset saved to '{output_file}'.")

if __name__ == "__main__":
    main()
