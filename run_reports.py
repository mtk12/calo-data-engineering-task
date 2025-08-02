import argparse
import gzip
import os

import pandas as pd

from analysis import run_complete_analysis
from parser import parse_logs, parse_balance_sync_message, parse_transaction
from user_analysis import analyze_all_users


def generate_transaction_data(df):
    records = []

    for ind, row in df.iterrows():
        parsed_message = parse_transaction(row['message'])
        if parsed_message != dict():
            parsed_message['request_id'] = row['dup_request_id']
            parsed_message['timestamp'] = row['timestamp']
            records.append(parsed_message)
    parsed_df = pd.DataFrame(records)
    parsed_df['timestamp'] = pd.to_datetime(parsed_df['timestamp'])
    return parsed_df


def generate_error_data(df):
    records = []
    for ind, row in df.iterrows():
        parsed_message = parse_balance_sync_message(row['message'])
        if parsed_message != dict():
            parsed_message['request_id'] = row['dup_request_id']
            parsed_message['timestamp'] = row['timestamp']
            records.append(parsed_message)
    error_df = pd.DataFrame(records)
    error_df['timestamp'] = pd.to_datetime(error_df['timestamp'])
    return error_df


def main(input_dir: str, output_dir: str):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    dfs = []

    for dir_path, dir_names, file_names in os.walk(input_dir):
        for file_name in file_names:
            if file_name.endswith('.gz'):
                file_path = os.path.join(dir_path, file_name)
                print(f"Reading: {file_path}")
                with gzip.open(file_path, 'rt') as f:
                    try:
                        log_text = f.read()
                        dfs.append(parse_logs(log_text))
                    except Exception as e:
                        print(f"Failed to read {file_path}: {e}")

    if dfs:
        all_data = pd.concat(dfs, ignore_index=True)
        print("Combined DataFrame shape:", all_data.shape)
    else:
        all_data = pd.DataFrame()
        print("No data found.")

    parsed_df = generate_transaction_data(all_data)
    error_df = generate_error_data(all_data[all_data['log_level'] == 'ERROR'])

    user_analysis_df = analyze_all_users(error_df, parsed_df)
    run_complete_analysis(parsed_df, error_df, user_analysis_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate balance sync analytics reports.")
    parser.add_argument("input_dir", help="Directory containing log files")
    parser.add_argument("output_dir", help="Directory to write reports to")
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
