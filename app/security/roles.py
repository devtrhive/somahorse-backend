# app/security/roles.py

from fastapi import Depends, HTTPException, status
from app.security.auth import get_current_user


def _check_role(user: dict, required: str):
    role = user.get("role") or user.get("custom_claims", {}).get("role")

    if role != required:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. {required} role required.",
        )


async def require_admin(user = Depends(get_current_user)):
    _check_role(user, "admin")
    return user


async def require_talent(user = Depends(get_current_user)):
    _check_role(user, "talent")
    return user


async def require_client(user = Depends(get_current_user)):
    _check_role(user, "client")
    return user
