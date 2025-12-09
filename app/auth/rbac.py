from fastapi import Depends, HTTPException
from app.auth.firebase import get_current_user


def require_roles(allowed_roles: list):
    def role_checker(user = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="User does not have the required role"
            )
        return user

    return role_checker
