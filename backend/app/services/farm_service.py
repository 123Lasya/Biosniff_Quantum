from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.user import User, UserRole
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut, FarmDetailOut
from app.repositories.farm_repo import FarmRepository
from app.repositories.farmer_repo import FarmerRepository


class FarmService:
    def __init__(self, db: Session):
        self.db = db
        self.farm_repo = FarmRepository(db)
        self.farmer_repo = FarmerRepository(db)

    def get_farm_by_id(self, farm_id: int, current_user: Optional[User] = None) -> Farm:
        farm = self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {farm_id} not found"
            )
        
        # If user is a farmer, verify ownership
        if current_user and current_user.role == UserRole.FARMER:
            farmer = self.farmer_repo.get_by_user_id(current_user.user_id)
            if not farmer or farm.farmer_id != farmer.farmer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this farm"
                )
        return farm

    def get_farms_for_farmer(self, farmer_id: int) -> List[Farm]:
        return self.farm_repo.get_by_farmer_id(farmer_id)

    def get_all_farms(self, skip: int = 0, limit: int = 100) -> List[Farm]:
        return self.farm_repo.get_all(skip=skip, limit=limit)

    def create_farm(self, farm_in: FarmCreate, current_user: User) -> Farm:
        # Determine farmer_id
        if current_user.role == UserRole.ADMIN:
            if not farm_in.farmer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="farmer_id must be provided by administrator"
                )
            farmer_id = farm_in.farmer_id
        else:
            farmer = self.farmer_repo.get_by_user_id(current_user.user_id)
            if not farmer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No farmer profile linked to this user"
                )
            farmer_id = farmer.farmer_id

        # Verify farmer exists
        farmer = self.farmer_repo.get_by_id(farmer_id)
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farmer with ID {farmer_id} not found"
            )

        return self.farm_repo.create(farm_in, farmer_id=farmer_id)

    def update_farm(self, farm_id: int, farm_in: FarmUpdate, current_user: User) -> Farm:
        farm = self.get_farm_by_id(farm_id, current_user=current_user)
        return self.farm_repo.update(farm, farm_in)

    def delete_farm(self, farm_id: int, current_user: User) -> bool:
        farm = self.get_farm_by_id(farm_id, current_user=current_user)
        return self.farm_repo.delete(farm)
