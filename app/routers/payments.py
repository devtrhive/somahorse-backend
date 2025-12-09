from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_roles
from app.services.mpesa import initiate_mpesa_payment, handle_mpesa_callback
from app.services.flutterwave import initiate_flutterwave_payment, handle_flutterwave_callback

router = APIRouter(prefix="/payments", tags=["Payments"])


# Request Models
class MpesaRequest(BaseModel):
    amount: float
    phone: str


class FlutterwaveRequest(BaseModel):
    amount: float
    email: str


# -------------------------
#  M-PESA Initiate Payment
# -------------------------
@router.post(
    "/mpesa/initiate",
    dependencies=[Depends(require_roles(["admin", "owner", "client"]))]
)
def mpesa_initiate(data: MpesaRequest, user=Depends(get_current_user)):
    return initiate_mpesa_payment(amount=data.amount, phone=data.phone)


# ------------------------------
#  M-PESA Callback (Webhook)
# ------------------------------
@router.post("/mpesa/callback")
def mpesa_callback(data: dict):
    return handle_mpesa_callback(data)


# ------------------------------
#  Flutterwave Initiate Payment
# ------------------------------
@router.get(
    "/flutterwave/status",
    dependencies=[Depends(require_roles(["admin", "owner", "client"]))]
)
def flutterwave_initiate(data: FlutterwaveRequest, user=Depends(get_current_user)):
    return initiate_flutterwave_payment(amount=data.amount, email=data.email)


# --------------------------------
#  Flutterwave Callback (Webhook)
# --------------------------------
@router.post("/flutterwave/callback")
def flutterwave_callback(data: dict):
    return handle_flutterwave_callback(data)
