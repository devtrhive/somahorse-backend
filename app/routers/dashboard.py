from fastapi import APIRouter, Depends
from datetime import datetime
from app.auth.rbac import require_roles
from app.auth.firebase import get_current_user

router = APIRouter(prefix="/transactions", tags=["Dashboard"])


@router.get("/feed", dependencies=[Depends(require_roles(["admin", "owner"]))])
async def transaction_feed(user=Depends(get_current_user)):
    
    # Temporary dummy data — real M-Pesa + Flutterwave next week
    dummy_transactions = [
        {
            "amount": 150.0,
            "payment_method": "M-Pesa",
            "msisdn": "254712345678",
            "created_at": datetime.utcnow(),
            "status": "SUCCESS"
        },
        {
            "amount": 500.0,
            "payment_method": "Flutterwave",
            "msisdn": "27831234567",
            "created_at": datetime.utcnow(),
            "status": "PENDING"
        }
    ]

    return {"data": dummy_transactions}
