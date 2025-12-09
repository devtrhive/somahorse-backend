from datetime import datetime
import uuid


def initiate_mpesa_payment(amount: float, phone: str):
    """
    Dummy M-PESA payment initiation.
    Replace with real Safaricom Daraja API integration (Week 6).
    """
    return {
        "provider": "M-PESA",
        "transaction_id": str(uuid.uuid4()),
        "amount": amount,
        "phone": phone,
        "status": "PENDING",
        "message": "M-PESA payment initiated (dummy).",
        "timestamp": datetime.utcnow().isoformat(),
    }


def handle_mpesa_callback(data: dict):
    """
    Dummy callback handler.
    This simulates the webhook M-PESA would send.
    """
    return {
        "provider": "M-PESA",
        "received_data": data,
        "status": "SUCCESS",
        "message": "M-PESA callback processed (dummy).",
        "timestamp": datetime.utcnow().isoformat(),
    }
