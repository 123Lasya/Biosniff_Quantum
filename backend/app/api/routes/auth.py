import os
import uuid
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User
from app.models.farmer import Farmer

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Farmer or Admin user"
)
def register(
    reg_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registers a new user account with hashed password and generates a Farmer profile
    if registered role is 'farmer'.
    """
    service = AuthService(db)
    return service.register_user(reg_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and obtain JWT access token"
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Validates user credentials and returns a signed JWT token containing:
    - access_token
    - token_type ('bearer')
    - user_id
    - role
    - farmer_id (if user is a farmer)
    """
    service = AuthService(db)
    return service.authenticate_user(login_data)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current authenticated user profile"
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the currently authenticated user's account details and associated farmer ID.
    Requires valid Bearer token.
    """
    farmer = db.query(Farmer).filter(Farmer.user_id == current_user.user_id).first()
    full_name = farmer.full_name if farmer else current_user.username
    profile_img = (farmer.profile_image if farmer else None) or current_user.profile_image_url
    return UserOut(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        farmer_id=farmer.farmer_id if farmer else None,
        full_name=full_name,
        profile_image_url=profile_img,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post(
    "/upload-avatar",
    summary="Upload user/farmer profile picture avatar"
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validates and uploads user avatar picture.
    Saves avatar under backend/uploads/avatars/ and updates DB user/farmer record.
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only JPEG, PNG, WEBP, and GIF images are allowed."
        )

    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(backend_dir, "uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"avatar_{current_user.user_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    filepath = os.path.join(upload_dir, filename)

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size (5MB)."
        )

    with open(filepath, "wb") as f:
        f.write(contents)

    image_url = f"/uploads/avatars/{filename}"

    # Update User and Farmer in DB
    current_user.profile_image_url = image_url
    farmer = db.query(Farmer).filter(Farmer.user_id == current_user.user_id).first()
    if farmer:
        farmer.profile_image = image_url
    
    db.commit()

    return {"url": image_url, "filename": filename}

