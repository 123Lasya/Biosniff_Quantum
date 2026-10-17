from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.farmer import Farmer
from app.schemas.farmer import FarmerCreate, FarmerUpdate


class FarmerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, farmer_id: int) -> Optional[Farmer]:
        return self.db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()

    def get_by_user_id(self, user_id: int) -> Optional[Farmer]:
        return self.db.query(Farmer).filter(Farmer.user_id == user_id).first()

    def get_by_email(self, email: str) -> Optional[Farmer]:
        return self.db.query(Farmer).filter(Farmer.email == email).first()

    def create(self, farmer_data: FarmerCreate) -> Farmer:
        db_farmer = Farmer(
            user_id=farmer_data.user_id,
            full_name=farmer_data.full_name,
            phone=farmer_data.phone,
            email=farmer_data.email,
            address=farmer_data.address,
            state=farmer_data.state,
            district=farmer_data.district,
            profile_image=farmer_data.profile_image
        )
        self.db.add(db_farmer)
        self.db.commit()
        self.db.refresh(db_farmer)
        return db_farmer

    def update(self, farmer: Farmer, update_data: FarmerUpdate) -> Farmer:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(farmer, key, value)
        self.db.commit()
        self.db.refresh(farmer)
        return farmer
