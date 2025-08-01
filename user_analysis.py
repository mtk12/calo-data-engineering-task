import pandas as pd


def analyze_user_data(user_id, error_data, parsed_transactions):
    # Filter data for the user
    user_error_data = error_data[error_data['userId'] == user_id].copy()
    user_transactions = parsed_transactions[parsed_transactions['userId'] == user_id].copy()

    # Convert timestamp columns to datetime
    user_error_data['timestamp'] = pd.to_datetime(user_error_data['timestamp'])
    user_transactions['timestamp'] = pd.to_datetime(user_transactions['timestamp'])

    # Sort by timestamp
    user_error_data = user_error_data.sort_values('timestamp')
    user_transactions = user_transactions.sort_values('timestamp')

    # Calculate analysis metrics
    first_error_transaction = user_error_data.iloc[0] if len(user_error_data) > 0 else None
    last_error_transaction = user_error_data.iloc[-1] if len(user_error_data) > 0 else None

    total_transactions = len(user_transactions)
    total_error_transactions = len(user_error_data)

    # Calculate total debit and credit losses from parsed transactions
    total_debit_loss = 0
    total_credit_loss = 0

    # Calculate loss from error data (subscriptionBalance - paymentBalance)
    user_error_data['subscriptionBalance'] = pd.to_numeric(user_error_data['subscriptionBalance'], errors='coerce')
    user_error_data['paymentBalance'] = pd.to_numeric(user_error_data['paymentBalance'], errors='coerce')
    user_error_data['loss'] = abs(user_error_data['subscriptionBalance'] - user_error_data['paymentBalance'])

    # Match error records with parsed transactions to get type-specific losses
    for _, error_row in user_error_data.iterrows():
        # Find matching transaction by request_id
        matching_transaction = user_transactions[user_transactions['request_id'] == error_row['request_id']]

        if not matching_transaction.empty:
            transaction_type = matching_transaction.iloc[0]['type']
            loss_amount = error_row['loss'] if pd.notna(error_row['loss']) else 0

            if transaction_type == 'DEBIT':
                total_debit_loss += loss_amount
            elif transaction_type == 'CREDIT':
                total_credit_loss += loss_amount
        else:
            # If no exact match, try timestamp matching
            error_time = error_row['timestamp']
            time_window = pd.Timedelta(seconds=5)
            matching_by_time = user_transactions[
                (user_transactions['timestamp'] >= error_time - time_window) &
                (user_transactions['timestamp'] <= error_time + time_window)
                ]

            if not matching_by_time.empty:
                transaction_type = matching_by_time.iloc[0]['type']
                loss_amount = error_row['loss'] if pd.notna(error_row['loss']) else 0

                if transaction_type == 'DEBIT':
                    total_debit_loss += loss_amount
                elif transaction_type == 'CREDIT':
                    total_credit_loss += loss_amount

    # Determine first error transaction reason by matching with parsed transactions
    first_error_reason = "Unknown"
    if first_error_transaction is not None:
        # Find the corresponding transaction in parsed data using request_id
        matching_transaction = user_transactions[
            user_transactions['request_id'] == first_error_transaction['request_id']]
        if not matching_transaction.empty:
            # Get the action and source from the matching transaction
            action = matching_transaction.iloc[0]['action']
            source = matching_transaction.iloc[0]['source']
            first_error_reason = f"{source} - {action}"
        else:
            # If no exact match, try to find by timestamp (within a small window)
            first_error_time = first_error_transaction['timestamp']
            time_window = pd.Timedelta(seconds=5)  # 5 second window
            matching_by_time = user_transactions[
                (user_transactions['timestamp'] >= first_error_time - time_window) &
                (user_transactions['timestamp'] <= first_error_time + time_window)
                ]
            if not matching_by_time.empty:
                action = matching_by_time.iloc[0]['action']
                source = matching_by_time.iloc[0]['source']
                first_error_reason = f"{source} - {action}"

    # Create analysis result
    analysis_result = {
        'UserId': user_id,
        'First_error_transaction': first_error_transaction['timestamp'].strftime(
            '%Y-%m-%d %H:%M:%S') if first_error_transaction is not None else 'N/A',
        'Last_error_transaction': last_error_transaction['timestamp'].strftime(
            '%Y-%m-%d %H:%M:%S') if last_error_transaction is not None else 'N/A',
        'Total_transactions': total_transactions,
        'Total_error_transactions': total_error_transactions,
        'Total_debit_loss': total_debit_loss,
        'Total_credit_loss': total_credit_loss,
        'First_error_transaction_reason': first_error_reason
    }

    return analysis_result


def analyze_all_users(error_df, parsed_df):
    unique_users = error_df['userId'].unique()
    print(f"Total unique users in error data: {len(unique_users)}")
    all_results = []

    for i, user_id in enumerate(unique_users):
        print(f"Analyzing user {i + 1}/{len(unique_users)}: {user_id}")

        try:
            result = analyze_user_data(user_id, error_df, parsed_df)
            all_results.append(result)
        except Exception as e:
            print(f"Error analyzing user {user_id}: {e}")
            # Add a default result for failed analysis
            all_results.append({
                'UserId': user_id,
                'First_error_transaction': 'N/A',
                'Last_error_transaction': 'N/A',
                'Total_transactions': 0,
                'Total_error_transactions': 0,
                'Total_debit_loss': 0,
                'Total_credit_loss': 0,
                'First_error_transaction_reason': 'Analysis failed'
            })

    result_df = pd.DataFrame(all_results)
    output_file = 'output_reports/all_users_analysis.csv'
    result_df.to_csv(output_file, index=False)

    print(f"\nAnalysis completed for all {len(unique_users)} users")
    print(f"Results saved to: {output_file}")
    return result_df
