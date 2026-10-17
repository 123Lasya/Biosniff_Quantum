from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate


class FarmRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, farm_id: int) -> Optional[Farm]:
        return self.db.query(Farm).filter(Farm.farm_id == farm_id).first()

    def get_by_farmer_id(self, farmer_id: int) -> List[Farm]:
        return self.db.query(Farm).filter(Farm.farmer_id == farmer_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Farm]:
        return self.db.query(Farm).offset(skip).limit(limit).all()

    def create(self, farm_data: FarmCreate, farmer_id: int) -> Farm:
        db_farm = Farm(
            farmer_id=farmer_id,
            farm_name=farm_data.farm_name,
            area=farm_data.area,
            crop=farm_data.crop,
            crop_variety=farm_data.crop_variety,
            growth_stage=farm_data.growth_stage,
            address=farm_data.address,
            latitude=farm_data.latitude,
            longitude=farm_data.longitude,
            boundary_geojson=farm_data.boundary_geojson,
            status=farm_data.status
        )
        self.db.add(db_farm)
        self.db.commit()
        self.db.refresh(db_farm)
        return db_farm

    def update(self, farm: Farm, update_data: FarmUpdate) -> Farm:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(farm, key, value)
        self.db.commit()
        self.db.refresh(farm)
        return farm

    def delete(self, farm: Farm) -> bool:
        self.db.delete(farm)
        self.db.commit()
        return True
