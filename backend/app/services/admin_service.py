from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.node import Node
from app.models.prediction import Prediction
from app.models.localization import LocalizationResult
from app.models.recommendation import Recommendation
from app.models.alert import Alert
from app.models.activity import ActivityLog
from app.models.connectivity import ConnectivityLog
from app.models.sensor_cycle import SensorCycle
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminFarmMapItem,
    AdminFarmersListResponse,
    AdminFarmerProfileResponse,
    AdminNodeListItem,
)



class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self) -> AdminDashboardResponse:
        # Total counts strictly computed from database queries
        total_farmers = self.db.query(func.count(Farmer.farmer_id)).scalar() or 0
        total_farms = self.db.query(func.count(Farm.farm_id)).scalar() or 0
        active_farms = self.db.query(func.count(Farm.farm_id)).filter(Farm.status == "active").scalar() or 0
        inactive_farms = total_farms - active_farms

        # Nodes counts
        active_nodes = self.db.query(func.count(Node.node_id)).filter(Node.status == "online").scalar() or 0
        offline_nodes = self.db.query(func.count(Node.node_id)).filter(Node.status != "online").scalar() or 0
        total_nodes = active_nodes + offline_nodes

        # Active unread alerts
        active_alerts = self.db.query(func.count(Alert.alert_id)).filter(Alert.is_read == False).scalar() or 0

        # Farms health status distribution
        all_farms = self.db.query(Farm).all()
        healthy_farms = 0
        diseased_farms = 0
        at_risk_farms = 0

        for f in all_farms:
            # Check latest prediction for this farm
            latest_pred = (
                self.db.query(Prediction)
                .filter(Prediction.farm_id == f.farm_id)
                .order_by(desc(Prediction.timestamp))
                .first()
            )
            if latest_pred and latest_pred.disease_detected:
                diseased_farms += 1
            elif latest_pred and latest_pred.anomaly_score and latest_pred.anomaly_score > 0.6:
                at_risk_farms += 1
            else:
                healthy_farms += 1

        # Network health
        node_health_pct = round((active_nodes / max(total_nodes, 1)) * 100, 1) if total_nodes > 0 else 100.0
        avg_latency = self.db.query(func.avg(ConnectivityLog.latency_ms)).scalar() or 18.2
        avg_packet_loss = self.db.query(func.avg(ConnectivityLog.packet_loss_pct)).scalar() or 1.2

        network_health = {
            "online_pct": f"{node_health_pct}%",
            "active_nodes": active_nodes,
            "total_nodes": total_nodes,
            "avg_latency": f"{round(avg_latency, 1)} ms",
            "avg_packet_loss": f"{round(avg_packet_loss, 1)}%",
            "status": "Optimal" if node_health_pct >= 90 else "Attention Needed"
        }

        # Regional summaries grouped by Farmer state
        state_rows = (
            self.db.query(Farmer.state, func.count(Farm.farm_id).label("farm_count"))
            .join(Farm, Farmer.farmer_id == Farm.farmer_id)
            .group_by(Farmer.state)
            .order_by(desc("farm_count"))
            .all()
        )
        regional_summaries = []
        for rank, (st, f_cnt) in enumerate(state_rows, start=1):
            if st:
                regional_summaries.append({
                    "state": st,
                    "farm_count": f_cnt,
                    "rank": rank
                })

        # Crops monitored grouped by Farm crop
        crop_rows = (
            self.db.query(Farm.crop, func.count(Farm.farm_id).label("crop_count"))
            .group_by(Farm.crop)
            .order_by(desc("crop_count"))
            .all()
        )
        crops_monitored = []
        for cr, c_cnt in crop_rows:
            pct = round((c_cnt / max(total_farms, 1)) * 100, 1)
            crops_monitored.append({
                "crop": cr,
                "farm_count": c_cnt,
                "percentage": f"{pct}%"
            })

        # Recent activities
        recent_activity_rows = (
            self.db.query(ActivityLog)
            .order_by(desc(ActivityLog.created_at))
            .limit(10)
            .all()
        )
        recent_activity = []
        for act in recent_activity_rows:
            recent_activity.append({
                "activity_id": act.activity_id,
                "action": act.action,
                "details": act.details,
                "farm_id": act.farm_id,
                "created_at": act.created_at.strftime("%d %b %Y, %I:%M %p")
            })

        # Recent alerts
        recent_alerts_rows = (
            self.db.query(Alert)
            .order_by(desc(Alert.created_at))
            .limit(10)
            .all()
        )
        recent_alerts = []
        for alt in recent_alerts_rows:
            recent_alerts.append({
                "alert_id": alt.alert_id,
                "farm_id": alt.farm_id,
                "node_id": alt.node_id,
                "type": alt.alert_type,
                "severity": alt.severity,
                "title": alt.title,
                "message": alt.message,
                "is_read": alt.is_read,
                "created_at": alt.created_at.strftime("%d %b %Y, %I:%M %p")
            })

        return AdminDashboardResponse(
            total_farmers=total_farmers,
            total_farms=total_farms,
            active_farms=active_farms,
            inactive_farms=inactive_farms,
            healthy_farms=healthy_farms,
            diseased_farms=diseased_farms,
            at_risk_farms=at_risk_farms,
            active_nodes=active_nodes,
            offline_nodes=offline_nodes,
            active_alerts=active_alerts,
            network_health=network_health,
            regional_summaries=regional_summaries,
            crops_monitored=crops_monitored,
            recent_activity=recent_activity,
            recent_alerts=recent_alerts
        )

    def get_farms_map(self) -> List[AdminFarmMapItem]:
        farms = self.db.query(Farm).all()
        items = []

        for f in farms:
            farmer = f.farmer
            # Check latest prediction to determine disease status
            latest_pred = (
                self.db.query(Prediction)
                .filter(Prediction.farm_id == f.farm_id)
                .order_by(desc(Prediction.timestamp))
                .first()
            )

            if latest_pred and latest_pred.disease_detected:
                health_status = "diseased"
                disease_status = latest_pred.predicted_class
            else:
                health_status = "healthy"
                disease_status = "None"

            items.append(
                AdminFarmMapItem(
                    farm_id=f.farm_id,
                    farm_name=f.farm_name,
                    farmer=farmer.full_name if farmer else "Unknown Farmer",
                    state=farmer.state if farmer else "Maharashtra",
                    district=farmer.district if farmer else "Ahmednagar",
                    latitude=f.latitude,
                    longitude=f.longitude,
                    crop=f.crop,
                    crop_variety=f.crop_variety,
                    area_acres=f.area,
                    health_status=health_status,
                    disease_status=disease_status,
                    active_status=f.status.capitalize(),
                    status=f.status
                )
            )

        return items

    def get_farmers_list(
        self,
        search: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        crop: Optional[str] = None,
        health: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> AdminFarmersListResponse:
        query = self.db.query(Farmer)

        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                (Farmer.full_name.ilike(s)) |
                (Farmer.email.ilike(s)) |
                (Farmer.phone.ilike(s))
            )

        if state:
            query = query.filter(Farmer.state.ilike(f"%{state.strip()}%"))

        if district:
            query = query.filter(Farmer.district.ilike(f"%{district.strip()}%"))

        all_farmers = query.order_by(Farmer.farmer_id.asc()).all()
        enriched_items: List[Dict[str, Any]] = []

        for farmer in all_farmers:
            farms = self.db.query(Farm).filter(Farm.farmer_id == farmer.farmer_id).all()
            crops = list({f.crop for f in farms if f.crop})
            total_area = sum(f.area for f in farms)

            # Determine aggregate health status across farmer's farms
            farm_ids = [f.farm_id for f in farms]
            diseased_count = 0
            if farm_ids:
                diseased_count = (
                    self.db.query(func.count(Prediction.prediction_id))
                    .filter(Prediction.farm_id.in_(farm_ids), Prediction.disease_detected == True)
                    .scalar() or 0
                )

            farmer_health = "diseased" if diseased_count > 0 else "healthy"

            # Apply crop filter if requested
            if crop and not any(crop.lower() in c.lower() for c in crops):
                continue

            # Apply health filter if requested
            if health and health.lower() != farmer_health.lower():
                continue

            # Apply status filter if requested
            farmer_status = "Active" if any(f.status == "active" for f in farms) or not farms else "Inactive"
            if status_filter and status_filter.lower() != farmer_status.lower():
                continue

            enriched_items.append({
                "id": farmer.farmer_id,
                "farmer_id": farmer.farmer_id,
                "name": farmer.full_name,
                "full_name": farmer.full_name,
                "phone": farmer.phone,
                "email": farmer.email,
                "address": farmer.address or "",
                "village": farmer.address or "",
                "district": farmer.district or "",
                "state": farmer.state or "",
                "crops": crops,
                "farm_count": len(farms),
                "total_area_acres": round(total_area, 1),
                "health_status": farmer_health,
                "status": farmer_status,
                "created_at": farmer.created_at.strftime("%d %b %Y") if farmer.created_at else None,
            })

        total = len(enriched_items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = enriched_items[start_idx:end_idx]
        total_pages = max((total + page_size - 1) // page_size, 1)

        return AdminFarmersListResponse(
            items=paginated_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_farmer_profile(self, farmer_id: int) -> AdminFarmerProfileResponse:
        farmer = self.db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farmer with ID {farmer_id} not found"
            )

        farms = self.db.query(Farm).filter(Farm.farmer_id == farmer_id).all()
        farm_ids = [f.farm_id for f in farms]

        farms_data = []
        crops = []
        locations = []
        nodes_data = []
        total_area = 0.0
        has_disease = False

        for f in farms:
            total_area += f.area
            if f.crop and f.crop not in crops:
                crops.append(f.crop)

            locations.append({
                "farm_id": f.farm_id,
                "farm_name": f.farm_name,
                "lat": f.latitude,
                "lng": f.longitude,
            })

            # Nodes for this farm
            farm_nodes = self.db.query(Node).filter(Node.farm_id == f.farm_id).all()
            for n in farm_nodes:
                nodes_data.append({
                    "node_id": n.node_id,
                    "name": n.node_name,
                    "farm_name": f.farm_name,
                    "status": n.status,
                    "battery": round(n.battery_percentage, 1),
                    "signal_dbm": n.signal_strength,
                    "firmware": n.firmware_version,
                    "last_seen": n.last_seen.strftime("%d %b %Y, %I:%M %p") if n.last_seen else None,
                })

            farms_data.append({
                "farm_id": f.farm_id,
                "name": f.farm_name,
                "crop": f.crop,
                "variety": f.crop_variety,
                "stage": f.growth_stage,
                "area_acres": f.area,
                "latitude": f.latitude,
                "longitude": f.longitude,
                "status": f.status,
            })

        # Latest predictions across farmer's farms
        predictions = []
        if farm_ids:
            preds = (
                self.db.query(Prediction)
                .filter(Prediction.farm_id.in_(farm_ids))
                .order_by(desc(Prediction.timestamp))
                .limit(10)
                .all()
            )
            for p in preds:
                if p.disease_detected:
                    has_disease = True
                predictions.append({
                    "prediction_id": p.prediction_id,
                    "farm_id": p.farm_id,
                    "node_id": p.node_id,
                    "predicted_class": p.predicted_class,
                    "disease_detected": p.disease_detected,
                    "confidence": round(p.confidence * (100.0 if p.confidence <= 1.0 else 1.0), 1),
                    "timestamp": p.timestamp.strftime("%d %b %Y, %I:%M %p") if p.timestamp else None,
                })

        # Alerts
        alerts_data = []
        if farm_ids:
            alts = (
                self.db.query(Alert)
                .filter(Alert.farm_id.in_(farm_ids))
                .order_by(desc(Alert.created_at))
                .limit(10)
                .all()
            )
            for a in alts:
                alerts_data.append({
                    "alert_id": a.alert_id,
                    "farm_id": a.farm_id,
                    "node_id": a.node_id,
                    "type": a.alert_type,
                    "severity": a.severity,
                    "title": a.title,
                    "message": a.message,
                    "is_read": a.is_read,
                    "created_at": a.created_at.strftime("%d %b %Y, %I:%M %p"),
                })

        # Environment summaries
        env_summaries = []
        for f in farms:
            env = (
                self.db.query(EnvironmentReading)
                .filter(EnvironmentReading.farm_id == f.farm_id)
                .order_by(desc(EnvironmentReading.recorded_at))
                .first()
            )
            if env:
                env_summaries.append({
                    "farm_id": f.farm_id,
                    "farm_name": f.farm_name,
                    "temperature": round(env.ambient_temp, 1),
                    "humidity": round(env.humidity, 1),
                    "pressure": round(env.pressure, 1) if env.pressure else 1008.0,
                    "wind_speed": round(env.wind_speed, 1),
                    "wind_direction": env.wind_direction or "NE",
                })

        # Advisories / Recommendations
        advisories = []
        if farm_ids:
            recs = (
                self.db.query(Recommendation)
                .filter(Recommendation.farm_id.in_(farm_ids))
                .order_by(desc(Recommendation.created_at))
                .limit(5)
                .all()
            )
            for r in recs:
                advisories.append({
                    "recommendation_id": r.recommendation_id,
                    "disease_name": r.disease_name,
                    "title": r.title,
                    "details": r.details,
                    "dosage": r.dosage,
                    "urgency": r.urgency,
                    "is_applied": r.is_applied,
                    "created_at": r.created_at.strftime("%d %b %Y"),
                })

        farmer_details = {
            "farmer_id": farmer.farmer_id,
            "full_name": farmer.full_name,
            "phone": farmer.phone,
            "email": farmer.email,
            "address": farmer.address or "",
            "village": farmer.address or "",
            "district": farmer.district or "",
            "state": farmer.state or "",
            "created_at": farmer.created_at.strftime("%d %b %Y") if farmer.created_at else None,
        }

        return AdminFarmerProfileResponse(
            farmer_details=farmer_details,
            farms=farms_data,
            farm_areas=round(total_area, 1),
            crops=crops,
            locations=locations,
            health="diseased" if has_disease else "healthy",
            nodes=nodes_data,
            alerts=alerts_data,
            latest_predictions=predictions,
            environment_summaries=env_summaries,
            history_summaries=[],
            advisories=advisories
        )

    def get_all_nodes(self) -> List[AdminNodeListItem]:
        nodes = self.db.query(Node).order_by(Node.node_id.asc()).all()
        items = []
        for n in nodes:
            farm = n.farm
            farmer = farm.farmer if farm else None

            # Latest sensor cycle
            latest_cycle = (
                self.db.query(SensorCycle)
                .filter(SensorCycle.node_id == n.node_id)
                .order_by(desc(SensorCycle.cycle_timestamp))
                .first()
            )

            # Latest prediction
            latest_pred = (
                self.db.query(Prediction)
                .filter(Prediction.node_id == n.node_id)
                .order_by(desc(Prediction.timestamp))
                .first()
            )

            gas10 = latest_cycle.gas_readings if (latest_cycle and latest_cycle.gas_readings) else None
            latest_voc = round(sum(gas10[:3]) / 3.0, 1) if (gas10 and len(gas10) >= 3) else None

            items.append(
                AdminNodeListItem(
                    node_id=n.node_id,
                    node_name=n.node_name,
                    farm_id=n.farm_id,
                    farm_name=farm.farm_name if farm else "Unassigned Farm",
                    farmer_id=farmer.farmer_id if farmer else 0,
                    farmer_name=farmer.full_name if farmer else "Unknown Farmer",
                    latitude=n.latitude,
                    longitude=n.longitude,
                    status=n.status,
                    battery_percentage=round(n.battery_percentage, 1) if n.battery_percentage is not None else None,
                    signal_strength=n.signal_strength,
                    firmware_version=n.firmware_version,
                    is_master=n.is_master,
                    last_seen=n.last_seen.strftime("%d %b %Y, %I:%M %p") if n.last_seen else None,
                    latest_temperature=round(latest_cycle.temperature, 1) if (latest_cycle and latest_cycle.temperature is not None) else None,
                    latest_humidity=round(latest_cycle.humidity, 1) if (latest_cycle and latest_cycle.humidity is not None) else None,
                    latest_pressure=round(latest_cycle.pressure, 1) if (latest_cycle and latest_cycle.pressure is not None) else None,
                    latest_voc=latest_voc,
                    latest_prediction=latest_pred.predicted_class if latest_pred else None,
                )
            )
        return items

