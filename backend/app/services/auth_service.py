from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.repositories.user_repo import UserRepository
from app.repositories.farmer_repo import FarmerRepository
from app.schemas.farmer import FarmerCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.farmer_repo = FarmerRepository(db)

    def register_user(self, reg_data: UserRegister) -> UserOut:
        # Check existing username
        if self.user_repo.get_by_username(reg_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already registered"
            )
        
        # Check existing email
        if self.user_repo.get_by_email(reg_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # Create base user
        db_user = self.user_repo.create(
            username=reg_data.username,
            email=reg_data.email,
            password=reg_data.password,
            role=reg_data.role,
            is_active=True
        )
        if reg_data.profile_image_url:
            db_user.profile_image_url = reg_data.profile_image_url
            self.db.commit()
            self.db.refresh(db_user)

        # If role is farmer, automatically provision farmer profile
        farmer_id = None
        full_name = reg_data.full_name or reg_data.username
        if reg_data.role == UserRole.FARMER:
            farmer_profile = self.farmer_repo.create(
                FarmerCreate(
                    user_id=db_user.user_id,
                    full_name=full_name,
                    phone=reg_data.phone or "N/A",
                    email=reg_data.email,
                    address=reg_data.address,
                    state=reg_data.state,
                    district=reg_data.district,
                    profile_image=reg_data.profile_image_url
                )
            )
            farmer_id = farmer_profile.farmer_id

            # Provision farm if crop / location info provided
            if reg_data.crop or reg_data.farm_name or reg_data.latitude:
                from app.schemas.farm import FarmCreate
                from app.services.farm_service import FarmService
                farm_service = FarmService(self.db)
                farm_service.create_farm(
                    FarmCreate(
                        farm_name=reg_data.farm_name or f"{full_name}'s Farm",
                        crop=reg_data.crop or "Rice",
                        crop_variety=reg_data.crop_variety,
                        area=reg_data.area or 5.0,
                        latitude=reg_data.latitude or 19.8321,
                        longitude=reg_data.longitude or 74.6521,
                        address=reg_data.address or f"{reg_data.district or ''}, {reg_data.state or ''}",
                        boundary_geojson=reg_data.boundary_geojson
                    ),
                    current_user=db_user
                )

        return UserOut(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            role=db_user.role.value,
            is_active=db_user.is_active,
            farmer_id=farmer_id,
            full_name=full_name,
            profile_image_url=db_user.profile_image_url,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

    def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        user = self.user_repo.get_by_username_or_email(login_data.username_or_email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        farmer = self.farmer_repo.get_by_user_id(user.user_id)
        farmer_id = farmer.farmer_id if farmer else None
        full_name = farmer.full_name if farmer else user.username
        profile_img = (farmer.profile_image if farmer else None) or user.profile_image_url

        # Build token payload with sub, role, and farmer_id
        token_payload = {
            "sub": str(user.user_id),
            "username": user.username,
            "role": user.role.value,
            "farmer_id": farmer_id
        }
        access_token = create_access_token(token_payload)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value,
            farmer_id=farmer_id,
            username=user.username,
            email=user.email,
            full_name=full_name,
            profile_image_url=profile_img
        )
