import argparse
import gzip
import os
import pandas as pd
from parser import parse_logs, parse_balance_sync_message, parse_transaction
from analysis import analyze_user_activity, generate_visualizations, create_consolidated_report


def generate_transaction_data(df):
    records = []

    for ind, row in df.iterrows():
        parsed_message = parse_transaction(row['message'])
        if parsed_message != dict():
            parsed_message['request_id'] = row['dup_request_id']
            parsed_message['timestamp'] = row['timestamp']
            records.append(parsed_message)
    parsed_df = pd.DataFrame(records)
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
    
    print(f"Parsed transaction data shape: {parsed_df.shape}")
    print(f"Error data shape: {error_df.shape}")
    
    # Save parsed data
    parsed_df.to_csv(f'{output_dir}/parsed_transactions.csv', index=False)
    error_df.to_csv(f'{output_dir}/error_data.csv', index=False)
    
    print("Saved parsed data to CSV files")
    
    # # Perform comprehensive analysis
    # if not parsed_df.empty:
    #     print("\n=== Starting Comprehensive Analysis ===")
        
    #     # Analyze user activity (will pick the most active user)
    #     analysis_results = analyze_user_activity(parsed_df, error_df)
        
    #     # Generate visualizations
    #     generate_visualizations(parsed_df, error_df, analysis_results['user_id'], output_dir)
        
    #     # Create consolidated report
    #     create_consolidated_report(analysis_results, output_dir)
        
    #     # Print summary
    #     print(f"\n=== Analysis Summary for User: {analysis_results['user_id']} ===")
    #     print(f"Total Transactions: {analysis_results['transaction_summary'].get('total_transactions', 0)}")
    #     print(f"Total Errors: {analysis_results['error_analysis'].get('total_errors', 0)}")
    #     print(f"Anomalies Detected: {analysis_results['anomalies']['total_anomalies']}")
    #     print(f"Recommendations: {len(analysis_results['recommendations'])}")
        
    #     if analysis_results['balance_analysis']:
    #         print(f"Final Balance: {analysis_results['balance_analysis'].get('final_balance', 0)}")
    #         print(f"Net Balance Change: {analysis_results['balance_analysis'].get('net_change', 0)}")
        
    #     print(f"\nReports generated in: {output_dir}")
    # else:
    #     print("No transaction data found for analysis")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate balance sync analytics reports.")
    parser.add_argument("input_dir", help="Directory containing log files")
    parser.add_argument("output_dir", help="Directory to write reports to")
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
