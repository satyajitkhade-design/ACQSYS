import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='get4_transaction_records.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TransactionRecord:
    def __init__(self, record_id, amount, date):
        self.record_id = record_id
        self.amount = amount
        self.date = date

    def __repr__(self):
        return f'TransactionRecord(record_id={self.record_id}, amount={self.amount}, date={self.date})'


def fetch_transaction_records(api_url):
    logging.info('Fetching transaction records from API')
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        logging.info('Fetched transaction records successfully')
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching transaction records: {e}')
        return None


def process_records(records):
    transaction_records = []
    logging.info('Processing transaction records')
    for record in records:
        try:
            transaction = TransactionRecord(record['id'], record['amount'], record['date'])
            transaction_records.append(transaction)
            logging.debug(f'Processed record: {transaction}')
        except KeyError as e:
            logging.error(f'Missing key in record: {e}')
    return transaction_records


def sort_records(records, key_attr):
    logging.info(f'Sorting records by {key_attr}')
    try:
        sorted_records = sorted(records, key=lambda x: getattr(x, key_attr))
        logging.info('Records sorted successfully')
        return sorted_records
    except AttributeError as e:
        logging.error(f'Error sorting records: {e}')
        return records


if __name__ == '__main__':
    API_URL = 'https://api.example.com/get4/transactions'
    records_data = fetch_transaction_records(API_URL)
    if records_data:
        processed_records = process_records(records_data)
        sorted_records = sort_records(processed_records, 'amount')
        logging.info(f'Sorted Transaction Records: {sorted_records}')
        # Further processing or exporting of sorted records can be done here
