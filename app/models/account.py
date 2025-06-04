# app/models/account.py
import json
import os # For path joining
from werkzeug.security import generate_password_hash # Let's add proper hashing back in

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This gets to 'app' directory
PROJECT_ROOT = os.path.dirname(BASE_DIR) # This gets to 'artproject' directory
ACCOUNTS_FILE = os.path.join(PROJECT_ROOT, 'accounts_data.json')


class Account:
    def __init__(self, accountID, name, email, phoneNumber, password_hash, orders=None):
        self.accountID = accountID
        self.name = name
        self.email = email
        self.phoneNumber = phoneNumber
        self.password_hash = password_hash # Storing the HASH
        self.orders = orders if orders is not None else []

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        from werkzeug.security import check_password_hash # Import here to avoid circularity if Account is imported elsewhere early
        return check_password_hash(self.password_hash, password)

    @classmethod
    def _load_accounts_data(cls):
        try:
            if not os.path.exists(ACCOUNTS_FILE): # Create file if it doesn't exist
                with open(ACCOUNTS_FILE, 'w') as f:
                    json.dump([], f) # Start with an empty list
                return []
            with open(ACCOUNTS_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [] # Ensure it's a list
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error: Could not load or parse {ACCOUNTS_FILE}. Returning empty list.")
            return [] # Return empty list on error to prevent crashes, create if not found

    @classmethod
    def _save_accounts_data(cls, accounts_list):
        try:
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts_list, f, indent=2)
        except IOError as e:
            print(f"Error saving accounts data: {e}")
            # Potentially raise the error or handle it more gracefully

    @classmethod
    def get_by_email(cls, email):
        accounts_data = cls._load_accounts_data()
        for acc_data in accounts_data:
            if acc_data['email'] == email:
                return cls(
                    accountID=acc_data.get('accountID'),
                    name=acc_data.get('name'),
                    email=acc_data.get('email'),
                    phoneNumber=acc_data.get('phoneNumber'),
                    password_hash=acc_data.get('password_hash'), # Load HASH
                    orders=acc_data.get('orders', []),
                )
        return None

    @classmethod
    def get_by_id(cls, account_id: str):
        """Returns an Account object by its ID, or None if not found."""
        accounts_data = cls._load_accounts_data()
        for acc_data in accounts_data:
            if acc_data.get('accountID') == account_id:
                # Ensure all args expected by __init__ are provided or have defaults
                return cls(
                    accountID=acc_data.get('accountID'),
                    name=acc_data.get('name'),
                    email=acc_data.get('email'),
                    phoneNumber=acc_data.get('phoneNumber'),
                    password_hash=acc_data.get('password_hash'),
                    orders=acc_data.get('orders', []),
                )
        return None

    @classmethod
    def create(cls, name, email, phoneNumber, password): # Changed method name for clarity
        """
        Creates a new account, hashes the password, and saves it to the JSON file.
        Returns the new Account object or raises ValueError if email exists.
        """
        accounts_list = cls._load_accounts_data()

        # Custom validation for email uniqueness (already in your form, but good to have here too)
        if cls.get_by_email(email): # Use existing get_by_email
            raise ValueError('That email address is already registered.')

        # Generate a simple new account ID (you might want a more robust system later)
        if accounts_list:
            last_id_num = int(accounts_list[-1]['accountID'].replace('acc', ''))
            new_id_num = last_id_num + 1
        else:
            new_id_num = 1
        new_account_id = f"acc{new_id_num:03d}"

        new_account_data = {
            "accountID": new_account_id,
            "name": name,
            "email": email,
            "phoneNumber": phoneNumber,
            "password_hash": generate_password_hash(password), # HASH THE PASSWORD
            "orders": [],
        }

        accounts_list.append(new_account_data)
        cls._save_accounts_data(accounts_list)

        # Return an instance of the Account class
        return cls(
            accountID=new_account_data['accountID'],
            name=new_account_data['name'],
            email=new_account_data['email'],
            phoneNumber=new_account_data['phoneNumber'],
            password_hash=new_account_data['password_hash'],
            orders=new_account_data['orders'],
        )