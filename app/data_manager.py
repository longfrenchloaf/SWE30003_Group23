import json
import os
import uuid # For generating other IDs like accountID, lineItemID

# Define root path for data files to be relative to the artproject directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This should point to artproject root

ORDER_COUNTER_FILE = os.path.join(BASE_DIR, 'order_counter.txt')
SALES_FILE = os.path.join(BASE_DIR, 'sales.json')
MERCHANDISE_FILE = os.path.join(BASE_DIR, 'merchandise_data.json')
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'accounts_data.json')
TRIPS_FILE = os.path.join(BASE_DIR, 'trips.json') 

def generate_unique_id(prefix=""):
    return prefix + str(uuid.uuid4().hex)[:8] # Shorter unique ID

# --- Order Counter ---
def get_next_order_id():
    try:
        with open(ORDER_COUNTER_FILE, 'r') as f:
            current_id = int(f.read().strip())
        next_id_str = f"ORD{current_id}" # Add prefix
        with open(ORDER_COUNTER_FILE, 'w') as f:
            f.write(str(current_id + 1))
        return next_id_str
    except FileNotFoundError:
        with open(ORDER_COUNTER_FILE, 'w') as f:
            f.write('1001') # Start from 1001 if file not found
        return "ORD1000"
    except ValueError: # If file content is not an int
         with open(ORDER_COUNTER_FILE, 'w') as f:
            f.write('1001')
         return "ORD1000"


# --- Generic JSON Read/Write ---
def read_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return [] # Return empty list if file doesn't exist
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {filepath}. Returning empty list.")
        return []


def write_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# --- Accounts Data ---
def get_all_accounts_data():
    return read_json_file(ACCOUNTS_FILE)

def save_all_accounts_data(accounts_data):
    write_json_file(ACCOUNTS_FILE, accounts_data)

def get_account_by_id_data(account_id):
    accounts = get_all_accounts_data()
    for acc in accounts:
        if acc.get("accountID") == account_id:
            return acc
    return None

def get_account_by_email_data(email):
    accounts = get_all_accounts_data()
    for acc in accounts:
        if acc.get("email") == email:
            return acc
    return None

# --- Merchandise Data ---
def get_all_merchandise_data():
    return read_json_file(MERCHANDISE_FILE)

def save_all_merchandise_data(merch_data): # For updating stock
    write_json_file(MERCHANDISE_FILE, merch_data)

def get_merchandise_by_id_data(merch_id):
    merchandise_list = get_all_merchandise_data()
    for item in merchandise_list:
        if item.get("merchandiseID") == merch_id:
            return item
    return None

# --- Sales/Orders Data ---
def get_all_sales_data(): # Sales data contains orders
    return read_json_file(SALES_FILE)

def save_all_sales_data(sales_data):
    write_json_file(SALES_FILE, sales_data)

def get_order_by_id_data(order_id):
    orders = get_all_sales_data()
    for order_data in orders:
        if order_data.get("orderID") == order_id:
            return order_data
    return None

# --- Trips Data ---
def get_all_trips_data():
    return read_json_file(TRIPS_FILE)

def save_all_trips_data(trips_data):
    write_json_file(TRIPS_FILE, trips_data)

def get_trip_by_id_data(trip_id): # Potentially useful, though not strictly required by this scenario
    trips = get_all_trips_data()
    for trip in trips:
        if trip.get("id") == trip_id:
            return trip
    return None