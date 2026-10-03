from enum import Enum


class StatusEmailMessage(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
