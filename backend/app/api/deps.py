from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.farmer import Farmer

# Bearer token scheme for user authentication
security = HTTPBearer(auto_error=True)
optional_security = HTTPBearer(auto_error=False)

# Hardware API Key header scheme for Master ESP32 Gateway
api_key_header = APIKeyHeader(name="X-Device-API-Key", auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates JWT Bearer token and returns the current active User.
    Raises 401 Unauthorized if invalid or expired.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.user_id == user_id_int).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Returns User if valid JWT is provided; None if omitted.
    Raises 401 if an invalid/expired token is provided.
    """
    if credentials is None:
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.user_id == user_id_int).first()
    if not user or not user.is_active:
        return None
    return user


def get_current_farmer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Farmer:
    """
    Ensures current authenticated user is a farmer and returns their Farmer profile.
    Admins are also permitted to access farmer endpoints if needed.
    """
    farmer = db.query(Farmer).filter(Farmer.user_id == current_user.user_id).first()
    if not farmer and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found for this account"
        )
    return farmer


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensures current authenticated user has administrator privileges.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation"
        )
    return current_user


def verify_device_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    Authenticates hardware Master ESP32 using the dedicated DEVICE_API_KEY.
    Ensures Master hardware does NOT use user JWTs.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Device-API-Key hardware authentication header",
        )
    if api_key != settings.DEVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid hardware device API key",
        )
    return api_key
