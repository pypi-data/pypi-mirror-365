import pandas as pd
import numpy as np
import os
import argparse

def transform_for_regression(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares the DataFrame for a regression task.
    For regression, the target is already numerical. We will keep all columns
    that are not of object type, as they might be useful features.
    """
    # Drop non-numeric columns, except for 'Date'
    cols_to_drop = [col for col in df.columns if df[col].dtype == 'object' and col != 'Date']
    df_regression = df.drop(columns=cols_to_drop)
    
    # Ensure 'target' column exists
    if 'target' not in df_regression.columns:
        raise ValueError("Target column 'target' not found in the DataFrame.")
        
    return df_regression

def transform_for_classification(df: pd.DataFrame, target_col='target', new_col_name='target_class') -> pd.DataFrame:
    """
    Prepares the DataFrame for a classification task by converting a numerical
    target into categorical classes ('up', 'down', 'flat').
    """
    df_classification = df.copy()

    if target_col not in df_classification.columns:
        raise ValueError(f"Target column '{target_col}' not found in the DataFrame.")

    # Create the categorical target column
    conditions = [
        df_classification[target_col] > 0,
        df_classification[target_col] < 0
    ]
    choices = ['up', 'down']
    df_classification[new_col_name] = np.select(conditions, choices, default='flat')
    
    # Drop the original numerical target
    df_classification = df_classification.drop(columns=[target_col])
    
    # Drop other non-numeric columns, except for 'Date' and the new target class
    cols_to_drop = [col for col in df_classification.columns if df_classification[col].dtype == 'object' and col not in ['Date', new_col_name]]
    df_classification = df_classification.drop(columns=cols_to_drop)
    
    return df_classification

def transform_for_forecasting(df: pd.DataFrame, series_id: str, target_col='target', timestamp_col='Date') -> pd.DataFrame:
    """
    Prepares the DataFrame for a forecasting task, conforming to Vertex AI's
    expected format (time_series_identifier, timestamp, target_value, [features...]).
    """
    df_forecasting = df.copy()

    # Ensure required columns exist
    if target_col not in df_forecasting.columns:
        raise ValueError(f"Target column '{target_col}' not found.")
    if timestamp_col not in df_forecasting.columns:
        # If 'Date' is the index, reset it to a column
        if df_forecasting.index.name == timestamp_col:
            df_forecasting.reset_index(inplace=True)
        else:
            raise ValueError(f"Timestamp column '{timestamp_col}' not found.")

    # Add time series identifier
    df_forecasting['time_series_identifier'] = series_id
    
    # Reorder columns to the standard format
    feature_cols = [col for col in df_forecasting.columns if col not in [timestamp_col, 'time_series_identifier', target_col]]
    final_cols = [timestamp_col, 'time_series_identifier', target_col] + feature_cols
    df_forecasting = df_forecasting[final_cols]

    # Drop other non-numeric columns
    cols_to_drop = [col for col in df_forecasting.columns if df_forecasting[col].dtype == 'object' and col not in [timestamp_col, 'time_series_identifier']]
    df_forecasting = df_forecasting.drop(columns=cols_to_drop)

    return df_forecasting

def main():
    """Main function to drive the data transformation."""
    parser = argparse.ArgumentParser(description="Transform dataset for Vertex AI training.")
    parser.add_argument(
        '-i', '--input-file', 
        type=str, 
        default='data/full/targets/mx/SPX500_D1_mz_tnd.csv',
        help='Input CSV file path.'
    )
    parser.add_argument(
        '-o', '--output-dir', 
        type=str, 
        default='data/vertex_ai',
        help='Output directory for transformed files.'
    )
    parser.add_argument(
        '--series-id', 
        type=str, 
        default='SPX500', 
        help='Time series identifier for forecasting.'
    )
    
    args = parser.parse_args()
    
    print(f"Starting data transformation for Vertex AI...")
    print(f"Input file: {args.input_file}")
    print(f"Output directory: {args.output_dir}")

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    try:
        df = pd.read_csv(args.input_file)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_file}")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # --- Regression ---
    try:
        df_regression = transform_for_regression(df.copy())
        regression_output_path = os.path.join(args.output_dir, 'data_regression.csv')
        df_regression.to_csv(regression_output_path, index=False)
        print(f"✅ Regression data saved to {regression_output_path}")
    except Exception as e:
        print(f"❌ Failed to create regression dataset: {e}")

    # --- Classification ---
    try:
        df_classification = transform_for_classification(df.copy())
        classification_output_path = os.path.join(args.output_dir, 'data_classification.csv')
        df_classification.to_csv(classification_output_path, index=False)
        print(f"✅ Classification data saved to {classification_output_path}")
    except Exception as e:
        print(f"❌ Failed to create classification dataset: {e}")

    # --- Forecasting ---
    try:
        df_forecasting = transform_for_forecasting(df.copy(), args.series_id)
        forecasting_output_path = os.path.join(args.output_dir, 'data_forecasting.csv')
        df_forecasting.to_csv(forecasting_output_path, index=False)
        print(f"✅ Forecasting data saved to {forecasting_output_path}")
    except Exception as e:
        print(f"❌ Failed to create forecasting dataset: {e}")

if __name__ == "__main__":
    main()