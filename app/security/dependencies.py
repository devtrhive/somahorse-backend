# app/security/dependencies.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional, Callable
from app.security.firebase import verify_id_token
from pydantic import BaseModel

bearer_scheme = HTTPBearer(auto_error=False)

class CurrentUser(BaseModel):
    uid: str
    email: Optional[str] = None
    role: Optional[str] = None
    mfa: Optional[bool] = False
    raw_claims: dict = {}

def get_token_from_header(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return credentials.credentials

def get_current_token(token: str = Depends(get_token_from_header)) -> dict:
    """
    Verifies the ID token and returns the decoded claims.
    Use check_revoked=True if you want to ensure token not revoked.
    """
    try:
        decoded = verify_id_token(token, check_revoked=False)
    except Exception as e:
        # Failed verification
        raise HTTPException(status_code=401, detail=f"Invalid auth token: {e}")

    return decoded

def get_current_user(decoded_token: dict = Depends(get_current_token)) -> CurrentUser:
    """
    Builds a CurrentUser object from decoded token claims.
    We expect custom claims to include 'role' and optionally 'mfa' flags.
    """
    uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    # Custom claims are at top-level of decoded_token (set via Admin SDK)
    role = decoded_token.get("role") or decoded_token.get("roles")  # support either
    mfa_flag = decoded_token.get("mfa")  # boolean custom claim if you set it

    return CurrentUser(uid=uid, email=email, role=role, mfa=bool(mfa_flag), raw_claims=decoded_token)

def require_role(required_role: str):
    """
    Dependency factory to enforce a role for a route.
    Example usage:
        @router.post(..., dependencies=[Depends(require_role("admin"))])
    Or within function:
        user: CurrentUser = Depends(require_role("talent"))
    """
    def _require_role(user: CurrentUser = Depends(get_current_user)):
        if not user.role:
            raise HTTPException(status_code=403, detail="No role assigned")
        # Support either string or list in claim
        if isinstance(user.role, (list, tuple, set)):
            if required_role not in user.role:
                raise HTTPException(status_code=403, detail="Insufficient role")
        else:
            if user.role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _require_role

def require_any_role(*allowed_roles: str):
    def _require_any(user: CurrentUser = Depends(get_current_user)):
        if not user.role:
            raise HTTPException(status_code=403, detail="No role assigned")
        if isinstance(user.role, (list, tuple, set)):
            if not any(r in user.role for r in allowed_roles):
                raise HTTPException(status_code=403, detail="Insufficient role")
        else:
            if user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _require_any

def require_mfa(user: CurrentUser = Depends(get_current_user)):
    """
    Ensures the user has completed MFA (as represented by a custom claim 'mfa' or
    other criteria). Because Firebase's ID token standard claims don't consistently
    surface MFA, we recommend setting a custom claim after a successful MFA flow.
    """
    if not user.mfa:
        raise HTTPException(status_code=403, detail="MFA required")
    return user
