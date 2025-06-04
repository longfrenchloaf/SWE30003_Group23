# artproject/app/models/order.py
from .enums import OrderStatus, PaymentStatus, TicketStatus
from .account import Account
from .payment import Payment
from .merchandise import Merchandise
from .trip import Trip # Import Trip model here
from app import data_manager # Your data persistence layer
from typing import List, Optional, Union, TYPE_CHECKING
from datetime import datetime, timezone
import json # For pretty printing in debug

if TYPE_CHECKING:
    from .account import Account # For type hinting
    from .trip import Trip # For type hinting
    from .merchandise import Merchandise # For type hinting


class SalesLineItem:
    def __init__(self, lineItemID: str,
                 item_id: str, # ID of the actual Ticket (Trip ID) or Merchandise object
                 item_type: str, # "ticket" or "merchandise"
                 quantity: int,
                 unit_price: float,
                 item_name: str,
                 line_item_status: str = TicketStatus.ACTIVE.value # Use Enum value strings consistently
                 ):
        self.lineItemID: str = lineItemID
        self._item_id: str = item_id
        self.item_type: str = item_type
        self.quantity: int = quantity
        self.unit_price: float = unit_price
        self.item_name: str = item_name
        # Store status as Enum for type safety and better comparisons
        try:
             self.line_item_status: TicketStatus = TicketStatus(line_item_status)
        except ValueError:
             print(f"Warning: Invalid line item status '{line_item_status}' for SLI {lineItemID}. Defaulting to PENDING.")
             self.line_item_status: TicketStatus = TicketStatus.PENDING


        self.lineTotal: float = self.unit_price * self.quantity

    @property
    def item_id(self) -> str:
        return self._item_id

    # @property
    # def item_object(self) -> Optional[Union[Trip, Merchandise]]: # Changed from Ticket to Trip
    #     """Fetches the associated Trip or Merchandise object."""
    #     # NOTE: Calling data_manager/get_by_id from here could be inefficient
    #     if self.item_type == "ticket":
    #         # Assuming item_id for tickets is the Trip ID
    #         return Trip.get_by_id(self._item_id)
    #     elif self.item_type == "merchandise":
    #         return Merchandise.get_by_id(self._item_id)
    #     return None

    def calculate_line_total(self) -> float:
        self.lineTotal = self.unit_price * self.quantity
        return self.lineTotal

    def get_quantity(self) -> int:
        return self.quantity

    # --- Add methods for status transitions ---
    def mark_rescheduled(self) -> bool:
        """Marks the line item status as RESCHEDULED."""
        if self.line_item_status == TicketStatus.ACTIVE:
            self.line_item_status = TicketStatus.RESCHEDULED
            # Optionally update name for clarity, although this could also be presentation logic
            # self.item_name = f"[RESCHEDULED] {self.item_name}"
            print(f"SLI {self.lineItemID} status set to RESCHEDULED.")
            return True
        print(f"Cannot mark SLI {self.lineItemID} as RESCHEDULED. Status is {self.line_item_status.value}.")
        return False

    def cancel(self) -> bool:
        """Marks the line item status as CANCELLED."""
        if self.line_item_status == TicketStatus.ACTIVE:
            self.line_item_status = TicketStatus.CANCELLED
            # Optionally update name
            # self.item_name = f"[CANCELLED] {self.item_name}"
            print(f"SLI {self.lineItemID} status set to CANCELLED.")
            return True
        print(f"Cannot cancel SLI {self.lineItemID}. Status is {self.line_item_status.value}.")
        return False

    def __repr__(self):
        return (f"<SalesLineItem {self.lineItemID} - Item: '{self.item_name[:30]}...' "
                f"({self.item_type}), Qty: {self.quantity}, UnitPrice: {self.unit_price:.2f}, "
                f"LineTotal: {self.lineTotal:.2f}, Status: {self.line_item_status.value}>") # Use .value for repr

    def to_dict(self) -> dict:
        print(f"DEBUG SalesLineItem.to_dict: SLI ID={self.lineItemID}, Name='{self.item_name[:30]}', SAVING Status={self.line_item_status.value}, LineTotal={self.lineTotal}") # Use .value for debug print
        return {
            "lineItemID": self.lineItemID,
            "item_id": self._item_id,
            "item_type": self.item_type,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "lineTotal": self.lineTotal,
            "line_item_status": self.line_item_status.value # Save Enum value as string
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional['SalesLineItem']:
        line_item_id = data.get("lineItemID")
        item_id = data.get("item_id")
        item_type = data.get("item_type")
        quantity = data.get("quantity")
        unit_price = data.get("unit_price")
        item_name = data.get("item_name", "N/A")
        line_item_status_str = data.get("line_item_status", TicketStatus.ACTIVE.value) # Default to Enum value string

        if not all([line_item_id, item_id, item_type, quantity is not None, unit_price is not None]):
            print(f"Warning: SalesLineItem data is missing required fields for creation: {data}")
            return None

        # Ensure quantity and unit_price are the correct types
        try:
             quantity = int(quantity)
             unit_price = float(unit_price)
        except (ValueError, TypeError):
             print(f"Warning: Invalid quantity or unit_price type for SLI {line_item_id}: {data}. Skipping.")
             return None

        return cls(
            lineItemID=line_item_id,
            item_id=item_id,
            item_type=item_type,
            item_name=item_name,
            quantity=quantity,
            unit_price=unit_price,
            line_item_status=line_item_status_str # Pass string to init, it will convert to Enum
        )

class Order:
    def __init__(self, orderID: str, placingAccountID: str,
                 orderLinetems: Optional[List[SalesLineItem]] = None,
                 totalAmount: float = 0.0,
                 payment: Optional[Payment] = None,
                 status: OrderStatus = OrderStatus.PENDING_PAYMENT,
                 cancellationRequests: Optional[List[str]] = None,
                 refundRequests: Optional[List[str]] = None,
                 orderTimestamp: Optional[datetime] = None):

        self.orderID: str = orderID
        self.placingAccountID: str = placingAccountID
        self.orderLinetems: List[SalesLineItem] = orderLinetems if orderLinetems is not None else []
        self.payment: Optional[Payment] = payment
        # Store status as Enum
        try:
            self.status: OrderStatus = OrderStatus(status) if isinstance(status, str) else status
        except ValueError:
             print(f"Warning: Invalid order status '{status}' for order {orderID}. Defaulting to PENDING_PAYMENT.")
             self.status: OrderStatus = OrderStatus.PENDING_PAYMENT

        self.cancellationRequests: List[str] = cancellationRequests if cancellationRequests is not None else []
        self.refundRequests: List[str] = refundRequests if refundRequests is not None else []
        self.orderTimestamp: datetime = orderTimestamp if orderTimestamp is not None else datetime.now(timezone.utc)

        # We will calculate totalAmount based on line items, but initialize or load it.
        self.totalAmount: float = totalAmount
        # Recalculate on load to ensure consistency, but typically you'd update on add/modify line item
        # self.update_total_amount()


    @property
    def placingAccount(self) -> Optional['Account']:
        # Ensure Account model has get_by_id
        return Account.get_by_id(self.placingAccountID) if hasattr(Account, 'get_by_id') else None

    def get_line_items(self) -> List[SalesLineItem]:
        return self.orderLinetems

    def add_line_item(self, sli: SalesLineItem):
        """Adds a SalesLineItem object to the order."""
        self.orderLinetems.append(sli)
        self.update_total_amount() # Recalculate total whenever an item is added

    def update_total_amount(self):
        current_payable_total = 0.0
        for item in self.orderLinetems:
            # Only count items towards the total based on their status.
            # Define what statuses are 'payable' or 'active' for the total.
            # Assuming only truly ACTIVE items contribute to the current total.
            if item.line_item_status == TicketStatus.ACTIVE: # Compare Enum values
                current_payable_total += item.lineTotal
        self.totalAmount = current_payable_total
        return self.totalAmount

    def get_status(self) -> OrderStatus:
        return self.status

    def update_status(self, new_status: OrderStatus, save_to_file: bool = True):
        """Updates the order status and optionally saves the order."""
        if not isinstance(new_status, OrderStatus):
             raise TypeError("new_status must be an OrderStatus enum member")
        self.status = new_status
        print(f"Order {self.orderID} status updated to {self.status.value}")
        if save_to_file:
            self.save()

    def process_payment(self, paymentMethodDetails: str):
        """
        Simulates processing payment for the order.
        Updates payment details, order status, and saves changes.
        Also handles stock/seat updates for active items upon successful payment.
        """
        self.update_total_amount() # Ensure total is correct before payment
        if self.status != OrderStatus.PENDING_PAYMENT or self.totalAmount <= 0:
            print(f"Cannot process payment for order {self.orderID}. Status: {self.status.value}, Total: {self.totalAmount}")
            return False

        payment_id = data_manager.generate_unique_id("pay")
        new_payment = Payment(
            paymentID=payment_id,
            relatedOrderID=self.orderID,
            amount=self.totalAmount,
            paymentMethodDetails=paymentMethodDetails,
            paymentStatus=PaymentStatus.PENDING # Start as PENDING
        )

        # Simulate transaction - call process_transaction method on Payment object
        if new_payment.process_transaction():
            self.payment = new_payment
            self.update_status(OrderStatus.PAID, save_to_file=False) # Update order status

            # --- Encapsulate stock/seat updates here AFTER successful payment ---
            # This ensures stock/seats are only reduced for paid orders
            for li in self.orderLinetems:
                if li.line_item_status == TicketStatus.ACTIVE:
                    if li.item_type == "merchandise":
                        merch = Merchandise.get_by_id(li.item_id)
                        if merch:
                            try:
                                # update_stock method in Merchandise should handle saving itself
                                merch.update_stock(-li.quantity)
                                print(f"Stock updated for merchandise {li.item_id}: -{li.quantity}")
                            except Exception as e:
                                print(f"Error updating stock for merchandise {li.item_id} during payment processing: {e}")
                                # Handle failure - potentially refund or mark order as failed/needs review
                                # For now, just print error
                        else:
                            print(f"Warning: Merchandise item {li.item_id} not found for stock update during payment.")
                    # NOTE: Ticket seat availability is handled during the initial purchase creation now (see create_ticket_order)
            # --- End Stock/Seat Updates ---

            self.save() # Save the order with updated status and payment
            print(f"Payment processed and order {self.orderID} marked PAID.")
            return True
        else:
            # Payment failed
            self.payment = new_payment # Store the failed payment attempt
            self.update_status(OrderStatus.FAILED, save_to_file=False)
            self.save()
            print(f"Payment processing failed for order {self.orderID}.")
            return False


    def get_primary_item_type_summary(self) -> str:
        if not self.orderLinetems:
            return "No Items"
        item_types_present = set(item.item_type.capitalize() for item in self.orderLinetems)
        if len(item_types_present) == 1:
            return item_types_present.pop()
        elif len(item_types_present) > 1:
            return f"Mixed ({', '.join(sorted(list(item_types_present)))})"
        return "Various Items"

    def get_item_summary_names(self, max_items_to_show=3) -> str:
        if not self.orderLinetems:
            return "N/A"

        active_item_names = [item.item_name for item in self.orderLinetems if item.line_item_status == TicketStatus.ACTIVE] # Compare Enum values

        items_to_summarize = active_item_names
        if not items_to_summarize:
            items_to_summarize = [item.item_name for item in self.orderLinetems] # Fallback to all items if no active

        if not items_to_summarize:
             return "No items in order"

        if len(items_to_summarize) > max_items_to_show:
            return ", ".join(items_to_summarize[:max_items_to_show]) + "..."
        return ", ".join(items_to_summarize)


    def to_dict(self) -> dict:
        self.update_total_amount() # Ensure total is fresh before saving
        return {
            "orderID": self.orderID,
            "placingAccountID": self.placingAccountID,
            "orderLinetems": [sli.to_dict() for sli in self.orderLinetems], # Assume line items are always valid objects
            "totalAmount": self.totalAmount,
            "payment": self.payment.to_dict() if self.payment else None,
            "status": self.status.value, # Save Enum value as string
            "cancellationRequests": self.cancellationRequests,
            "refundRequests": self.refundRequests,
            "orderTimestamp": self.orderTimestamp.isoformat()
        }

    def save(self):
        """Saves the current Order object to the data source."""
        print(f"DEBUG Order.save(): Saving Order {self.orderID} with status {self.status.value}")
        all_orders_data = data_manager.get_all_sales_data()
        order_dict_to_save = self.to_dict()

        updated_all_orders_data = []
        found = False
        for existing_order_dict in all_orders_data:
            if existing_order_dict.get("orderID") == self.orderID:
                updated_all_orders_data.append(order_dict_to_save)
                found = True
            else:
                updated_all_orders_data.append(existing_order_dict)
        if not found:
            updated_all_orders_data.append(order_dict_to_save)

        try:
            data_manager.save_all_sales_data(updated_all_orders_data)
            print(f"DEBUG Order.save(): Successfully saved Order {self.orderID}")
        except Exception as e:
            print(f"CRITICAL ERROR Order.save(): Failed to save Order {self.orderID}: {e}")
            # Handle save error - maybe attempt rollback or log more severely
            raise # Re-raise the exception so the route can catch it


    @classmethod
    def from_dict(cls, data: dict) -> Optional['Order']:
        if not data or not data.get("orderID") or not data.get("placingAccountID"):
             print(f"Warning: Order data is missing essential keys for creation: {data}")
             return None

        line_items_data = data.get("orderLinetems", [])
        line_items_objs = [sli_obj for li_data in line_items_data if (sli_obj := SalesLineItem.from_dict(li_data))]

        payment_obj = Payment.from_dict(data.get("payment")) # Use .get for safety

        status_str = data.get("status", OrderStatus.PENDING_PAYMENT.value)
        try:
            status_enum = OrderStatus(status_str)
        except ValueError:
            print(f"Warning: Invalid order status string '{status_str}' for order {data.get('orderID')}. Defaulting to PENDING_PAYMENT.")
            status_enum = OrderStatus.PENDING_PAYMENT

        order_timestamp_str = data.get("orderTimestamp")
        order_timestamp_obj = datetime.now(timezone.utc) # Default to current time
        if order_timestamp_str:
            try:
                if order_timestamp_str.endswith('Z'):
                    order_timestamp_str = order_timestamp_str[:-1] + '+00:00'
                dt_obj = datetime.fromisoformat(order_timestamp_str)
                # Ensure timestamp is UTC and offset-aware
                order_timestamp_obj = dt_obj.astimezone(timezone.utc) if dt_obj.tzinfo else dt_obj.replace(tzinfo=timezone.utc)
            except ValueError as e:
                print(f"Warning: Invalid order timestamp format '{order_timestamp_str}' for order {data.get('orderID')}: {e}. Using current time.")

        return cls(
            orderID=data["orderID"],
            placingAccountID=data["placingAccountID"],
            orderLinetems=line_items_objs,
            totalAmount=float(data.get("totalAmount", 0.0)), # Use .get for safety
            payment=payment_obj,
            status=status_enum,
            cancellationRequests=data.get("cancellationRequests", []), # Use .get for safety
            refundRequests=data.get("refundRequests", []),         # Use .get for safety
            orderTimestamp=order_timestamp_obj
        )

    @staticmethod
    def get_by_id(order_id: str) -> Optional['Order']:
        """Loads a specific Order object by ID."""
        order_data = data_manager.get_order_by_id_data(order_id)
        return Order.from_dict(order_data)

    @staticmethod
    def get_all() -> List['Order']:
        """Loads all Order objects."""
        all_orders_data = data_manager.get_all_sales_data()
        return [order_obj for o_data in all_orders_data if (order_obj := Order.from_dict(o_data))]

    @staticmethod
    def get_orders_by_account_id(account_id: str) -> List['Order']:
         """Loads Order objects for a specific account ID."""
         all_orders = Order.get_all()
         return [order for order in all_orders if order.placingAccountID == account_id]

    def find_line_item_by_sli_id(self, line_item_id: str) -> Optional[SalesLineItem]:
        """Finds a specific SalesLineItem object within this order by its ID."""
        for item in self.orderLinetems:
            if item.lineItemID == line_item_id:
                return item
        return None

    def reschedule_ticket_line_item(self, original_line_item_id: str, new_trip_obj: 'Trip') -> bool:
        """
        Marks an original ticket line item as RESCHEDULED and adds a new line item
        for the new trip. Adjusts availability on both old and new trips.
        Saves the order and affected trips.
        Returns True on success, False otherwise.
        """
        print(f"DEBUG Order.reschedule_ticket_line_item: START - Rescheduling SLI ID: {original_line_item_id} for Order {self.orderID} to New Trip {new_trip_obj.id}")

        original_sli_found = self.find_line_item_by_sli_id(original_line_item_id)

        if not original_sli_found or original_sli_found.item_type != "ticket":
            print(f"  ERROR: Ticket sales line item {original_line_item_id} not found or not a ticket.")
            return False

        # --- Call method on SLI instead of direct attribute access ---
        # The check for ACTIVE status is now inside mark_rescheduled
        if not original_sli_found.mark_rescheduled():
             print(f"  ERROR: Could not mark SLI {original_line_item_id} as RESCHEDULED (not active?).")
             return False

        # --- Check availability on the new trip ---
        if not new_trip_obj.check_availability(1): # Assuming 1 ticket per reschedule
            print(f"  ERROR: Not enough seats on new trip {new_trip_obj.id}.")
            # Should we revert the original SLI status? For simplicity now, we won't,
            # but in a real system, transactionality or compensation is needed.
            return False

        # --- Get the original trip to update availability ---
        original_trip_obj = Trip.get_by_id(original_sli_found.item_id) # Fetch original trip by its ID stored in SLI
        if not original_trip_obj:
             print(f"  WARNING: Original trip {original_sli_found.item_id} not found for availability update.")
             # Continue with reschedule, but flag this issue.
             pass # Or handle as a critical error depending on requirements


        # --- Perform the updates ---
        # The original SLI status was updated by the call above: original_sli_found.mark_rescheduled()

        if original_trip_obj:
            # update_availability handles saving the trip
             original_trip_obj.update_availability(+original_sli_found.quantity) # Add seats back (quantity should be 1 for tickets)
             print(f"  Original Trip {original_trip_obj.id} availability updated.")

        # update_availability handles saving the trip
        new_trip_obj.update_availability(-1) # Deduct seat from new trip
        print(f"  New Trip {new_trip_obj.id} availability updated.")


        # Create a new Sales Line Item for the new ticket
        new_sli_id = data_manager.generate_unique_id("sli")
        new_ticket_sli = SalesLineItem(
            lineItemID=new_sli_id,
            item_id=new_trip_obj.id, # Item ID is the NEW trip ID
            item_type="ticket",
            item_name=f"Ticket: {new_trip_obj.route} - {new_trip_obj.date} {new_trip_obj.time}",
            quantity=1,
            unit_price=new_trip_obj.price, # Use price of the new trip
            line_item_status=TicketStatus.ACTIVE.value # New ticket starts as ACTIVE
        )

        self.add_line_item(new_ticket_sli) # This appends and calls update_total_amount()

        try:
            self.save() # Save the modified order (with updated statuses and new line item)
            print(f"DEBUG Order.reschedule_ticket_line_item: END - Order {self.orderID} save successful.")
            return True
        except Exception as e:
            print(f"CRITICAL ERROR Order.reschedule_ticket_line_item: Failed to save Order {self.orderID} during reschedule: {e}")
            # Need robust rollback here in a real system (e.g., undo availability changes and SLI status)
            return False


    def initiate_cancellation(self) -> bool:
        """
        Initiates cancellation process for the order.
        Marks active items as CANCELLED, updates stock/seats,
        updates order status, and potentially initiates a refund.
        Saves the order and affected items.
        Returns True if cancellation process initiated (at least one item cancelled), False otherwise.
        """
        print(f"DEBUG Order.initiate_cancellation(): START - Order {self.orderID}")

        if self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.FAILED]:
            print(f"  Cannot cancel order {self.orderID}. Current status: {self.status.value}")
            return False

        self.cancellationRequests.append(f"Cancellation requested by user on {datetime.now(timezone.utc).isoformat()}")

        items_successfully_cancelled_count = 0
        any_item_restocked = False

        for sli in self.orderLinetems:
            # --- Call method on SLI instead of direct attribute access ---
            # The check for ACTIVE status is now inside cancel()
            if sli.cancel(): # Attempt to cancel the item
                 items_successfully_cancelled_count += 1
                 print(f"  Successfully cancelled SLI {sli.lineItemID}.")

                 # --- Restock/Release Seats ---
                 if sli.item_type == "ticket":
                     # For tickets, item_id is the Trip ID in the current design
                     trip_obj = Trip.get_by_id(sli.item_id)
                     if trip_obj:
                         try:
                              # update_availability method in Trip should handle saving itself
                             trip_obj.update_availability(+sli.quantity) # Add seats back (quantity is typically 1 for tickets)
                             print(f"  Returned seat(s) to trip {trip_obj.id}.")
                         except Exception as e:
                             print(f"  Error updating trip availability for {trip_obj.id} during cancellation: {e}")
                             # Log or handle partial failure
                     else:
                         print(f"  Warning: Trip {sli.item_id} not found for availability update during cancellation.")

                 elif sli.item_type == "merchandise":
                     merch_obj = Merchandise.get_by_id(sli.item_id)
                     if merch_obj:
                         try:
                             # update_stock method in Merchandise should handle saving itself
                             merch_obj.update_stock(+sli.quantity) # Add stock back
                             any_item_restocked = True
                             print(f"  Restocked {sli.quantity} of merchandise {merch_obj.merchandiseID}.")
                         except Exception as e:
                             print(f"  Error updating merchandise stock for {merch_obj.merchandiseID} during cancellation: {e}")
                             # Log or handle partial failure
                     else:
                         print(f"  Warning: Merchandise {sli.item_id} not found for stock update during cancellation.")
                 # --- End Restock/Release Seats ---
            else:
                 print(f"  SLI {sli.lineItemID} was not cancelled (status was not ACTIVE).")


        if items_successfully_cancelled_count == 0:
            print(f"  No active items were successfully cancelled in order {self.orderID}.")
            # If no items were cancelled by this process, perhaps update order status
            # to CANCELLED anyway if *all* items are already in a non-ACTIVE state?
            all_items_non_active = all(sli.line_item_status != TicketStatus.ACTIVE for sli in self.orderLinetems)
            if all_items_non_active and self.status != OrderStatus.CANCELLED:
                 self.update_status(OrderStatus.CANCELLED, save_to_file=True) # Save status change
                 self.update_total_amount() # Recalculate total (should be 0)
            return False # Indicate that no *new* cancellations occurred

        self.update_total_amount() # Recalculate total based on remaining active items (should be 0 if all were cancelled)

        # Determine final order status after cancellation
        # If all items in the order are now in a CANCELLED state, mark the order as CANCELLED.
        all_items_are_cancelled_state = all(sli.line_item_status == TicketStatus.CANCELLED for sli in self.orderLinetems)
        if all_items_are_cancelled_state:
             self.update_status(OrderStatus.CANCELLED, save_to_file=False)
        # Else, if some items remain non-cancelled (e.g., already completed, pending, etc.),
        # the order status might remain PAID or move to a PARTIALLY_CANCELLED state (if implemented).
        # With current logic, if any non-cancelled items exist, the status stays as is unless already handled.
        # For this code, if any items are not CANCELLED after the loop, the order status is not set to CANCELLED.


        # Handle refund if the order was paid
        if self.payment and self.payment.paymentStatus == PaymentStatus.SUCCESSFUL:
             self.initiate_refund(reason=f"User cancellation request processed on {datetime.now(timezone.utc).isoformat()}")
             # initiate_refund calls save() internally, so we don't call save() here
             print(f"  Initiated refund for order {self.orderID}.")
        else:
             # If not paid, simply cancel and save
             try:
                self.save() # Save the order with updated line item statuses and order status
                print(f"DEBUG Order.initiate_cancellation(): Order {self.orderID} saved after cancellation (no refund needed).")
             except Exception as e:
                print(f"CRITICAL ERROR Order.initiate_cancellation(): Failed to save Order {self.orderID} after cancellation (no refund): {e}")
                # Handle save error
                raise

        print(f"DEBUG Order.initiate_cancellation(): END - Order {self.orderID}")
        return True # Indicate that cancellations were processed


    def initiate_refund(self, reason: str = "Requested refund"):
        """
        Simulates initiating a refund for the order's successful payment.
        Updates payment status and records refund request.
        Saves the order. Assumes items were handled before calling this (e.g., via cancellation).
        """
        print(f"DEBUG Order.initiate_refund(): START - Order {self.orderID}")
        if not (self.payment and self.payment.paymentStatus == PaymentStatus.SUCCESSFUL):
            print(f"  Cannot refund order {self.orderID}. No successful payment to refund.")
            # Potentially update status to CANCELLED if not already, and save
            if self.status != OrderStatus.CANCELLED:
                 self.update_status(OrderStatus.CANCELLED, save_to_file=True)
            return

        self.refundRequests.append(f"Refund for {self.payment.amount} requested on {datetime.now(timezone.utc).isoformat()} due to: {reason}")
        self.payment.paymentStatus = PaymentStatus.REFUNDED # Simulate refund success

        # Ensure order status reflects cancellation if it was not already (common path to refund is cancellation)
        if self.status != OrderStatus.CANCELLED:
             self.update_status(OrderStatus.CANCELLED, save_to_file=False)

        try:
             self.save() # Save the order with updated payment status and refund request
             print(f"DEBUG Order.initiate_refund(): Order {self.orderID} saved after refund initiated.")
        except Exception as e:
             print(f"CRITICAL ERROR Order.initiate_refund(): Failed to save Order {self.orderID} after refund: {e}")
             # Handle save error
             raise

        print(f"DEBUG Order.initiate_refund(): END - Order {self.orderID}")


    # --- Factory methods to create new orders ---
    @staticmethod
    def create_ticket_order(account_id: str, trip_id: str, payment_method_details: str) -> Optional['Order']:
        """
        Creates a new order for a single ticket purchase.
        Handles fetching trip details, checking availability, updating trip availability,
        creating order and line item, processing payment, and saving.
        Returns the created Order object on success, None on failure.
        Raises exceptions for specific failures like not enough seats.
        """
        account = Account.get_by_id(account_id)
        if not account:
            print(f"ERROR create_ticket_order: Account {account_id} not found.")
            return None # Account not found is a critical failure

        trip = Trip.get_by_id(trip_id)
        if not trip:
            print(f"ERROR create_ticket_order: Trip {trip_id} not found.")
            return None # Trip not found is a critical failure

        if not trip.check_availability(1):
             print(f"ERROR create_ticket_order: Not enough seats on trip {trip_id}.")
             raise ValueError(f"Not enough seats available for trip {trip.route} on {trip.date} {trip.time}.")

        order_id = data_manager.get_next_order_id()
        new_order = Order(orderID=order_id, placingAccountID=account_id)

        # Add ticket line item - item_id for tickets is the Trip ID
        sli_id = data_manager.generate_unique_id("sli")
        ticket_sli = SalesLineItem(
             lineItemID=sli_id,
             item_id=trip.id,
             item_type="ticket",
             item_name=f"Ticket: {trip.route} - {trip.date} {trip.time}",
             quantity=1,
             unit_price=trip.price,
             line_item_status=TicketStatus.ACTIVE.value # New tickets start as ACTIVE
        )
        new_order.add_line_item(ticket_sli) # Adds the SLI and updates order total

        # --- Update trip availability immediately when the ticket is added/allocated ---
        # update_availability method handles saving the trip data
        try:
             trip.update_availability(-1)
             print(f"Trip {trip.id} availability updated successfully.")
        except Exception as e:
             print(f"CRITICAL ERROR create_ticket_order: Failed to update trip availability for {trip.id}: {e}")

             raise RuntimeError(f"Failed to update seat availability for trip {trip.id}.") from e


        # Process payment - this will update order status to PAID and call new_order.save()
        try:
             payment_success = new_order.process_payment(payment_method_details)
             if not payment_success:
                 print(f"ERROR create_ticket_order: Payment processing failed for order {new_order.orderID}.")
                 # process_payment already saves the order with status FAILED, so return the order.
                 return new_order
        except Exception as e:
             print(f"CRITICAL ERROR create_ticket_order: Exception during payment processing for order {new_order.orderID}: {e}")
             # process_payment might not have been called or saved. Attempt to mark as FAILED if possible.
             if new_order.status == OrderStatus.PENDING_PAYMENT:
                  new_order.update_status(OrderStatus.FAILED, save_to_file=True)
             raise RuntimeError(f"Error during payment processing for new order {new_order.orderID}.") from e


        print(f"DEBUG create_ticket_order: Successfully created and processed Order {new_order.orderID}")
        return new_order # Return the successfully created order object


    @staticmethod
    def create_merchandise_order(account_id: str, items_with_quantities: List[dict], payment_method_details: str) -> Optional['Order']:
        """
        Creates a new order for merchandise items.
        Takes a list of dictionaries: [{'merch_id': '...', 'quantity': N}, ...].
        Handles fetching merchandise, checking stock, creating order and line items,
        processing payment (which updates stock), and saving.
        Returns the created Order object on success, None on critical failure.
        Raises exceptions for specific failures like not enough stock.
        """
        account = Account.get_by_id(account_id)
        if not account:
            print(f"ERROR create_merchandise_order: Account {account_id} not found.")
            return None # Critical failure

        order_id = data_manager.get_next_order_id()
        new_order = Order(orderID=order_id, placingAccountID=account_id)

        merchandise_line_items = []
        items_for_stock_update_check = {} # Store merch objects and final quantities before updating

        for item_info in items_with_quantities:
            merch_id = item_info.get('merch_id')
            quantity = item_info.get('quantity', 0)
            if not merch_id or quantity <= 0:
                 continue # Skip invalid entries

            merch_obj = Merchandise.get_by_id(merch_id)
            if not merch_obj:
                # If one item isn't found, should the whole order fail? Let's fail for now.
                print(f"ERROR create_merchandise_order: Merchandise item {merch_id} not found.")
                raise ValueError(f"Merchandise item {merch_id} not found.")

            # Check availability *before* adding to order
            if not merch_obj.check_availability(quantity):
                 print(f"ERROR create_merchandise_order: Not enough stock for {merch_obj.name} ({merch_id}).")
                 raise ValueError(f"Not enough stock for {merch_obj.name}. Requested: {quantity}, Available: {merch_obj.stockLevel}")

            # Create Sales Line Item object
            sli_id = data_manager.generate_unique_id("sli")
            merch_sli = SalesLineItem(
                 lineItemID=sli_id,
                 item_id=merch_obj.merchandiseID,
                 item_type="merchandise",
                 item_name=merch_obj.get_name(),
                 quantity=quantity,
                 unit_price=merch_obj.get_price(),
                 line_item_status=TicketStatus.ACTIVE.value # Initial status is ACTIVE
            )
            merchandise_line_items.append(merch_sli)
            items_for_stock_update_check[merch_id] = {'obj': merch_obj, 'quantity': quantity}


        if not merchandise_line_items:
            print("ERROR create_merchandise_order: No valid merchandise items provided.")
            return None # No items to order

        # Add all valid line items to the order
        for sli in merchandise_line_items:
             new_order.add_line_item(sli) # This updates the order total

        # Process payment - this will update order status to PAID and call new_order.save()
        # The logic to update merchandise stock is already in process_payment for ACTIVE merchandise items
        try:
             payment_success = new_order.process_payment(payment_method_details)
             if not payment_success:
                 print(f"ERROR create_merchandise_order: Payment processing failed for order {new_order.orderID}.")
                 # process_payment already saves the order with status FAILED.
                 # Stock wasn't deducted because process_payment checks for SUCCESSFUL status before updating stock.
                 return new_order # Return the order object with FAILED status
        except Exception as e:
            print(f"CRITICAL ERROR create_merchandise_order: Exception during payment processing for order {new_order.orderID}: {e}")
             # process_payment might not have been called or saved. Attempt to mark as FAILED if possible.
            if new_order.status == OrderStatus.PENDING_PAYMENT:
                 new_order.update_status(OrderStatus.FAILED, save_to_file=True)
            raise RuntimeError(f"Error during payment processing for new order {new_order.orderID}.") from e


        print(f"DEBUG create_merchandise_order: Successfully created and processed Order {new_order.orderID}")
        return new_order # Return the successfully created order object


    # --- END Factory methods ---