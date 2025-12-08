from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from typing import Optional
from app.database import get_db
# For demo: pretend we decode token and get user id and role from firebase/auth.
# Replace with your real auth integration

security = HTTPBearer()

def get_current_user(token = Depends(security)):
    # stub: decode token and return a user object/dict
    # In production: verify via Firebase Admin SDK and fetch user & roles from DB
    # Example return:
    return {"id": 1, "email": "dev@example.com", "role": "admin"}

def requires_role(required_role: str):
    def role_checker(user = Depends(get_current_user)):
        if not user or user.get("role") != required_role:
            raise HTTPException(status_code=403, detail={"error":"forbidden","message":f"Insufficient role: {required_role} required"})
        return user
    return role_checker
