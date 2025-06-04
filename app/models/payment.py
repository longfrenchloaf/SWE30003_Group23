# artproject/app/models/payment.py
from .enums import PaymentStatus
from datetime import datetime, timezone
from app import data_manager 
from typing import Optional

class Payment:
    def __init__(self, paymentID: str, relatedOrderID: str, amount: float,
                 paymentMethodDetails: str,
                 timestamp: Optional[datetime] = None,
                 paymentStatus: PaymentStatus = PaymentStatus.PENDING):
        self.paymentID: str = paymentID
        self.relatedOrderID: str = relatedOrderID
        self.amount: float = amount
        self.timestamp: datetime = timestamp if timestamp is not None else datetime.now(timezone.utc)
        self.paymentMethodDetails: str = paymentMethodDetails
        # Ensure paymentStatus is an Enum member
        try:
            self.paymentStatus: PaymentStatus = PaymentStatus(paymentStatus) if isinstance(paymentStatus, str) else paymentStatus
        except ValueError:
            print(f"Warning: Invalid payment status '{paymentStatus}' for payment {paymentID}. Defaulting to PENDING.")
            self.paymentStatus: PaymentStatus = PaymentStatus.PENDING


    def get_timestamp(self) -> datetime:
        """Returns the payment timestamp as a datetime object."""
        return self.timestamp

    def process_transaction(self) -> bool:
        """
        Simulates processing the payment.
        Updates status to SUCCESSFUL and sets/updates the timestamp.
        """
        print(f"Processing payment {self.paymentID} for order {self.relatedOrderID} amount {self.amount}...")
        # Simulate success (in a real app, this involves external calls)
        self.paymentStatus = PaymentStatus.SUCCESSFUL
        self.timestamp = datetime.now(timezone.utc)
        print(f"Payment {self.paymentID} successful.")
        return True # Assume success for simulation


    def get_status(self) -> PaymentStatus:
        return self.paymentStatus

    def __repr__(self):
        return f"<Payment {self.paymentID} for Order {self.relatedOrderID} - Status: {self.paymentStatus.value}>"

    def to_dict(self) -> dict:
        """Converts the Payment object to a dictionary for JSON serialization."""
        # Use "timestamp" as the standard key for consistency going forward
        return {
            "paymentID": self.paymentID,
            "relatedOrderID": self.relatedOrderID,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(), # Save as "timestamp"
            "paymentMethodDetails": self.paymentMethodDetails,
            "paymentStatus": self.paymentStatus.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional['Payment']:
        """
        Creates a Payment object from a dictionary (e.g., when loading from JSON).
        Handles both "timestamp" and "paymentTimestamp" for backward compatibility.
        Returns None if essential data is missing or invalid.
        """
        if not data:
            return None

        payment_id = data.get("paymentID")
        related_order_id = data.get("relatedOrderID")
        amount = data.get("amount")
        payment_method_details = data.get("paymentMethodDetails")
        # --- Check for both 'timestamp' (new) and 'paymentTimestamp' (old) ---
        timestamp_str = data.get("timestamp", data.get("paymentTimestamp"))
        payment_status_str = data.get("paymentStatus", PaymentStatus.PENDING.value) # Default to enum value string

        if not all([payment_id, related_order_id, amount is not None, payment_method_details]):
            print(f"Warning: Payment.from_dict missing essential keys in data: {data}. Missing: {[k for k in ['paymentID', 'relatedOrderID', 'amount', 'paymentMethodDetails'] if data.get(k) is None or data.get(k)=='']}. Returning None.")
            return None # Or raise an error

        try:
            # Ensure amount is float
            amount = float(amount)
        except (ValueError, TypeError):
             print(f"Error: Invalid amount value '{amount}' for payment {payment_id}. Returning None.")
             return None

        # Parse timestamp string
        timestamp_dt = datetime.now(timezone.utc) # Default to current time if parsing fails
        if timestamp_str:
            try:
                if isinstance(timestamp_str, str):
                    if timestamp_str.endswith('Z'):
                        timestamp_dt = datetime.fromisoformat(timestamp_str[:-1] + '+00:00')
                    else:
                        timestamp_dt = datetime.fromisoformat(timestamp_str)
                    # Ensure it's offset-aware and UTC
                    if timestamp_dt.tzinfo is None:
                        timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)
                    else:
                        timestamp_dt = timestamp_dt.astimezone(timezone.utc)
                elif isinstance(timestamp_str, datetime):
                    timestamp_dt = timestamp_str
                    if timestamp_dt.tzinfo is None:
                        timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)
                    else:
                        timestamp_dt = timestamp_dt.astimezone(timezone.utc)
                else:
                     print(f"Warning: Invalid timestamp type '{type(timestamp_str)}' in payment data {payment_id}. Defaulting timestamp.")

            except ValueError as e:
                print(f"Warning: Error parsing timestamp '{timestamp_str}' for payment {payment_id}: {e}. Using current time.")
            except Exception as e: # Catch any other unexpected errors during parsing
                 print(f"Warning: Unexpected error parsing timestamp '{timestamp_str}' for payment {payment_id}: {e}. Using current time.")

        # Convert status string to Enum, default if invalid
        try:
            payment_status_enum = PaymentStatus(payment_status_str)
        except ValueError:
            print(f"Warning: Invalid payment status string '{payment_status_str}' for payment {payment_id}. Defaulting to PENDING.")
            payment_status_enum = PaymentStatus.PENDING


        return cls(
            paymentID=payment_id,
            relatedOrderID=related_order_id,
            amount=amount,
            timestamp=timestamp_dt, # Pass the parsed datetime object
            paymentMethodDetails=payment_method_details,
            paymentStatus=payment_status_enum # Pass the Enum member
        )