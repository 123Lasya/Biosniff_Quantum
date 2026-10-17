from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate, NodeStatusUpdate


class NodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, node_id: str) -> Optional[Node]:
        return self.db.query(Node).filter(Node.node_id == node_id).first()

    def get_by_farm_id(self, farm_id: int) -> List[Node]:
        return self.db.query(Node).filter(Node.farm_id == farm_id).order_by(Node.node_id.asc()).all()

    def count_nodes_in_farm(self, farm_id: int) -> int:
        return self.db.query(Node).filter(Node.farm_id == farm_id).count()

    def create(self, node_data: NodeCreate) -> Node:
        db_node = Node(
            node_id=node_data.node_id,
            farm_id=node_data.farm_id,
            node_name=node_data.node_name,
            latitude=node_data.latitude,
            longitude=node_data.longitude,
            status=node_data.status,
            battery_percentage=node_data.battery_percentage,
            signal_strength=node_data.signal_strength,
            firmware_version=node_data.firmware_version,
            is_master=node_data.is_master,
            last_seen=datetime.now(timezone.utc)
        )
        self.db.add(db_node)
        self.db.commit()
        self.db.refresh(db_node)
        return db_node

    def update(self, node: Node, update_data: NodeUpdate) -> Node:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(node, key, value)
        self.db.commit()
        self.db.refresh(node)
        return node

    def update_telemetry(
        self,
        node: Node,
        battery_percentage: Optional[float] = None,
        signal_strength: Optional[float] = None,
        status: Optional[str] = None
    ) -> Node:
        if battery_percentage is not None:
            node.battery_percentage = battery_percentage
        if signal_strength is not None:
            node.signal_strength = signal_strength
        if status is not None:
            node.status = status
        node.last_seen = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete(self, node: Node) -> bool:
        self.db.delete(node)
        self.db.commit()
        return True
