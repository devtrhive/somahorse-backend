from datetime import datetime
import uuid


def initiate_flutterwave_payment(amount: float, email: str):
    """
    Dummy Flutterwave payment initiation.
    Real API integration will be implemented in Week 6.
    """
    return {
        "provider": "Flutterwave",
        "transaction_id": str(uuid.uuid4()),
        "amount": amount,
        "email": email,
        "status": "PENDING",
        "message": "Flutterwave payment initiated (dummy).",
        "timestamp": datetime.utcnow().isoformat(),
    }


def handle_flutterwave_callback(data: dict):
    """
    Dummy webhook callback handler for Flutterwave.
    """
    return {
        "provider": "Flutterwave",
        "received_data": data,
        "status": "SUCCESS",
        "message": "Flutterwave callback processed (dummy).",
        "timestamp": datetime.utcnow().isoformat(),
    }
