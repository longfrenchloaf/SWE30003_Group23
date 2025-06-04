from enum import Enum

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class OrderStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    COMPLETED = "COMPLETED" 
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class TicketStatus(Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    INVALID = "INVALID"
    RESCHEDULED = "RESCHEDULED"
    PENDING = "PENDING" # e.g. pending confirmation