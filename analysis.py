import warnings

import matplotlib.pyplot as plt
import seaborn as sns

from reports.excel_report import insert_chart_to_excel

warnings.filterwarnings('ignore')

# Set style for better looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def transaction_count_over_period(parsed_df):
    """Transaction count over the period bar chart"""
    plt.figure(figsize=(7, 4))

    # Group by date and count transactions
    daily_transactions = parsed_df.groupby(parsed_df['timestamp'].dt.date).size()

    plt.bar(daily_transactions.index, daily_transactions.values, alpha=0.7, color='skyblue')
    plt.title('Transaction Count Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Transactions', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/transaction_count_over_period.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Transaction Analysis",
                          "output_reports/transaction_count_over_period.png", "B2")


def credit_transactions_over_period(parsed_df):
    """Credit transactions over the period"""
    plt.figure(figsize=(7, 4))

    # Filter credit transactions
    credit_df = parsed_df[parsed_df['type'] == 'CREDIT']
    daily_credits = credit_df.groupby(credit_df['timestamp'].dt.date).size()

    plt.bar(daily_credits.index, daily_credits.values, alpha=0.7, color='lightgreen')
    plt.title('Credit Transactions Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Credit Transactions', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/credit_transactions_over_period.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Transaction Analysis",
                          "output_reports/credit_transactions_over_period.png", "B60")


def debit_transactions_over_period(parsed_df):
    """Debit transactions over the period"""
    plt.figure(figsize=(7, 4))

    # Filter debit transactions
    debit_df = parsed_df[parsed_df['type'] == 'DEBIT']
    daily_debits = debit_df.groupby(debit_df['timestamp'].dt.date).size()

    plt.bar(daily_debits.index, daily_debits.values, alpha=0.7, color='lightcoral')
    plt.title('Debit Transactions Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Debit Transactions', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/debit_transactions_over_period.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Transaction Analysis",
                          "output_reports/debit_transactions_over_period.png", "B118")


def transactions_by_action_over_period(parsed_df):
    """Transaction count by action"""
    plt.figure(figsize=(7, 4))

    # Get top 15 actions by count
    action_counts = parsed_df['action'].value_counts().head(15)

    # Create horizontal bar chart
    plt.barh(range(len(action_counts)), action_counts.values, alpha=0.7, color='skyblue')
    plt.yticks(range(len(action_counts)), action_counts.index)
    plt.title('Transaction Count by Action', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Transactions', fontsize=12)
    plt.ylabel('Action', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/transactions_by_action_over_period.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Transaction Analysis",
                          "output_reports/transactions_by_action_over_period.png", "B176")


def top_users_transacting(parsed_df):
    """Top users transacting"""
    plt.figure(figsize=(7, 4))

    # Get top 10 users by transaction count
    top_users = parsed_df['userId'].value_counts().head(10)

    plt.bar(range(len(top_users)), top_users.values, alpha=0.7, color='gold')
    plt.xticks(range(len(top_users)), top_users.index, rotation=45, ha="right")  # Set actual user IDs on the x-axis
    plt.title('Top 10 Users by Transaction Count', fontsize=16, fontweight='bold')
    plt.ylabel('Number of Transactions', fontsize=12)
    plt.xlabel('Users', fontsize=12)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/top_users_transacting.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Transaction Analysis",
                          "output_reports/top_users_transacting.png", "B234")


def error_transactions_over_period(error_df):
    """Error transactions over the period with anomaly detection"""
    plt.figure(figsize=(7, 4))

    # Group by date and count errors
    daily_errors = error_df.groupby(error_df['timestamp'].dt.date).size()

    # Calculate anomaly threshold (2 standard deviations from mean)
    mean_errors = daily_errors.mean()
    std_errors = daily_errors.std()
    threshold = mean_errors + (2 * std_errors)

    # Plot daily errors
    bars = plt.bar(daily_errors.index, daily_errors.values, alpha=0.7, color='lightblue')

    # Highlight anomalies
    anomaly_dates = daily_errors[daily_errors > threshold]
    for date in anomaly_dates.index:
        idx = list(daily_errors.index).index(date)
        bars[idx].set_color('red')
        bars[idx].set_alpha(0.8)

    # Add threshold line
    plt.axhline(y=threshold, color='red', linestyle='--', alpha=0.7, label=f'Anomaly Threshold ({threshold:.1f})')

    plt.title('Error Transactions Over Time (Anomalies Highlighted)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Error Transactions', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/error_transactions_over_period.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Error Analysis",
                          "output_reports/error_transactions_over_period.png", "B2")


def error_transactions_by_action(error_df, parsed_df, top_n=10):
    """Top Error Transactions by Action"""
    plt.figure(figsize=(7, 4))

    # Merge error data with parsed transactions to get action information
    error_with_action = error_df.merge(
        parsed_df[['request_id', 'action']],
        on='request_id',
        how='left'
    )

    # Count errors by action
    error_by_action = error_with_action['action'].value_counts()

    # Get the top N actions (default is 10)
    top_error_by_action = error_by_action.head(top_n)

    plt.bar(top_error_by_action.index, top_error_by_action.values, alpha=0.7, color='skyblue')
    plt.title(f'Top {top_n} Error Transactions by Action', fontsize=16, fontweight='bold')
    plt.xlabel('Action', fontsize=12)
    plt.ylabel('Number of Errors', fontsize=12)
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()
    plt.savefig(f'output_reports/top_{top_n}_error_transactions_by_action.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Error Analysis",
                          f"output_reports/top_{top_n}_error_transactions_by_action.png", "B60")


def top_users_error_transactions(error_df):
    """Top users with error transactions"""
    plt.figure(figsize=(7, 4))

    # Get top 20 users by error count
    top_error_users = error_df['userId'].value_counts().head(20)

    plt.barh(range(len(top_error_users)), top_error_users.values, alpha=0.7, color='lightcoral')
    plt.yticks(range(len(top_error_users)), top_error_users.index)
    plt.title('Top 20 Users by Error Transaction Count', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Error Transactions', fontsize=12)
    plt.ylabel('Users', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/top_users_error_transactions.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Error Analysis",
                          "output_reports/top_users_error_transactions.png", "B118")


def total_debit_credit_loss(user_analysis_df):
    """Total overall debit and credit loss"""
    plt.figure(figsize=(7, 4))

    # Calculate totals
    total_debit_loss = user_analysis_df['Total_debit_loss'].sum()
    total_credit_loss = user_analysis_df['Total_credit_loss'].sum()

    # Create bar chart
    categories = ['Total Debit Loss', 'Total Credit Loss']
    values = [total_debit_loss, total_credit_loss]
    colors = ['lightcoral', 'lightgreen']

    bars = plt.bar(categories, values, color=colors, alpha=0.7)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                 f'{value:,.2f}', ha='center', va='bottom', fontweight='bold')

    plt.title('Total Debit vs Credit Loss', fontsize=16, fontweight='bold')
    plt.ylabel('Loss Amount', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/total_debit_credit_loss.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Error Analysis",
                          "output_reports/total_debit_credit_loss.png", "B176")


def first_error_reason_count(user_analysis_df):
    """First error transaction reason count (ignore nan - nan)"""
    plt.figure(figsize=(7, 4))

    # Filter out 'nan - nan' and count reasons
    reasons = user_analysis_df[user_analysis_df['First_error_transaction_reason'] != 'nan - nan']
    reason_counts = reasons['First_error_transaction_reason'].value_counts()

    # Create horizontal bar chart for better readability
    plt.barh(range(len(reason_counts)), reason_counts.values, alpha=0.7, color='skyblue')
    plt.yticks(range(len(reason_counts)), reason_counts.index)
    plt.title('First Error Transaction Reasons', fontsize=16, fontweight='bold')
    plt.xlabel('Count', fontsize=12)
    plt.ylabel('Error Reason', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output_reports/first_error_reason_count.png', dpi=300, bbox_inches='tight')
    insert_chart_to_excel("output_reports/", "analysis.xlsx", "Error Analysis",
                          "output_reports/total_debit_credit_loss.png", "B234")


def run_complete_analysis(parsed_df, error_df, user_analysis_df):
    """Run all analysis functions"""
    print("=== Starting Complete Dataset Analysis ===\n")
    print("\n=== Transaction Analysis ===")
    transaction_count_over_period(parsed_df)
    credit_transactions_over_period(parsed_df)
    debit_transactions_over_period(parsed_df)
    transactions_by_action_over_period(parsed_df)
    top_users_transacting(parsed_df)

    print("\n=== Error Analysis ===")
    error_transactions_over_period(error_df)
    error_transactions_by_action(error_df, parsed_df)
    top_users_error_transactions(error_df)

    print("\n=== Loss Analysis ===")
    total_debit_credit_loss(user_analysis_df)
    first_error_reason_count(user_analysis_df)

    print("\n=== Analysis Complete ===")
    print("All charts have been saved to output_reports/ directory")
