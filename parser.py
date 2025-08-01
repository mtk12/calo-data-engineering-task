import re

import pandas as pd

LOG_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T[0-9:.]+Z)'
    r'(?:\s+(?P<type>\S+))?'
    r'(?:\s+RequestId:\s*(?P<request_id>[\w-]+))?'
    r'(?:\s+Version:\s*(?P<version>\S+))?'
    r'(?:\t(?P<dup_timestamp>\d{4}-\d{2}-\d{2}T[0-9:.]+Z))?'
    r'(?:\t(?P<dup_request_id>[\w-]+))?'
    r'(?:\t(?P<log_level>\w+))?'
)

TRANSACTION_PATTERN = {
    'id': r"id: '([^']*)'",
    'type': r"type: '([^']*)'",
    'source': r"source: '([^']*)'",
    'action': r"action: '([^']*)'",
    'userId': r"userId: '([^']*)'",
    'paymentBalance': r"paymentBalance: (\d+)",
    'updatePaymentBalance': r"updatePaymentBalance: (true|false)",
    'metadata': r"metadata: '([^']*)'",
    'currency': r"currency: '([^']*)'",
    'amount': r"amount: (\d+)",
    'vat': r"vat: (\d+)",
    'oldBalance': r"oldBalance: (\d+)",
    'newBalance': r"newBalance: (\d+)",
}


def parse_logs(log_text):
    entries = re.split(r'(?=^\d{4}-\d{2}-\d{2}T[0-9:.]+Z)', log_text, flags=re.MULTILINE)

    parsed_records = []

    for entry in entries:
        if not entry.strip():
            continue
        lines = entry.splitlines()
        first = lines[0]
        m = LOG_PATTERN.match(first)
        rec = {k: None for k in
               ['timestamp', 'type', 'request_id', 'version', 'dup_timestamp', 'dup_request_id', 'log_level']}
        if m:
            rec.update({k: m.group(k) for k in rec.keys()})
        if m:
            inline = first[m.end():].strip()
        else:
            inline = first
        message = inline
        if len(lines) > 1:
            message += '\n' + '\n'.join(lines[1:])
        rec['message'] = message
        rec['raw_entry'] = entry
        parsed_records.append(rec)

    # Create DataFrame
    df = pd.DataFrame(parsed_records)
    return df


def parse_transaction(message):
    record = {}
    for key, pat in TRANSACTION_PATTERN.items():
        m = re.search(pat, message)
        if key == 'id' and not m:
            break
        if not m:
            record[key] = None
        else:
            val = m.group(1)
            if key in ['paymentBalance', 'amount', 'vat', 'oldBalance', 'newBalance']:
                record[key] = int(val)
            elif key == 'updatePaymentBalance':
                record[key] = True if val == 'true' else False
            else:
                record[key] = val

    return record


def parse_balance_sync_message(message):
    uid = re.search(r"userId:\s*'([^']+)'", message)
    sub = re.search(r"subscriptionBalance:\s*([0-9]+(?:\.[0-9]+)?)", message)
    pay = re.search(r"paymentBalance:\s*([0-9]+(?:\.[0-9]+)?)", message)
    if uid:
        return {
            "userId": uid.group(1) if uid else None,
            "subscriptionBalance": float(sub.group(1)) if sub else None,
            "paymentBalance": float(pay.group(1)) if pay else None
        }
    else:
        return {}