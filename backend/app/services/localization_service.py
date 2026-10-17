import math
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.node import Node
from app.repositories.localization_repo import LocalizationRepository
from app.repositories.farm_repo import FarmRepository
from app.repositories.node_repo import NodeRepository


def circular_mean_degrees(angles: List[float]) -> float:
    """
    Computes the circular mean of an array of wind direction angles in degrees.
    Prevents naive linear averaging across the 0/360 degree boundary.
    e.g. mean([350, 10]) = 0.0 (North), not 180.0 (South).
    """
    if not angles:
        return 0.0
    sin_sum = sum(math.sin(math.radians(a)) for a in angles)
    cos_sum = sum(math.cos(math.radians(a)) for a in angles)
    mean_rad = math.atan2(sin_sum, cos_sum)
    mean_deg = math.degrees(mean_rad) % 360.0
    return round(mean_deg, 2)


def gps_to_metric(lat: float, lon: float, origin_lat: float, origin_lon: float) -> Tuple[float, float]:
    """
    Converts geographic coordinates (latitude, longitude) to local metric coordinates
    relative to a local farm origin (meters East, meters North) using Equirectangular flat-earth projection.
    """
    R = 6371000.0  # Earth's mean radius in meters
    origin_lat_rad = math.radians(origin_lat)
    x = (math.radians(lon) - math.radians(origin_lon)) * R * math.cos(origin_lat_rad)
    y = (math.radians(lat) - math.radians(origin_lat)) * R
    return round(x, 3), round(y, 3)


def metric_to_gps(x: float, y: float, origin_lat: float, origin_lon: float) -> Tuple[float, float]:
    """
    Converts local metric coordinates (meters East, meters North) back to WGS84
    geographic coordinates (latitude, longitude).
    """
    R = 6371000.0
    origin_lat_rad = math.radians(origin_lat)
    lat = origin_lat + math.degrees(y / R)
    lon = origin_lon + math.degrees(x / (R * math.cos(origin_lat_rad)))
    return round(lat, 6), round(lon, 6)


class LocalizationService:
    """
    Bio-Sniff MVP Wind-Aware Grid-Based Source Likelihood Estimation Service.
    
    Determines likely VOC emission source coordinates and affected crop zone
    when one or more nodes report crop disease. Transforms node GPS into local
    metric coordinates (East/North), evaluates candidate source positions against
    a wind-advected Gaussian-plume influence model, and returns both local and
    GPS coordinates.
    
    Disclaimer: This provides an empirical localization/source-likelihood score
    for decision support and does not claim plant-level triangulation accuracy.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.localization_repo = LocalizationRepository(db) if db else None
        self.farm_repo = FarmRepository(db) if db else None
        self.node_repo = NodeRepository(db) if db else None

    def estimate_source_location(
        self,
        farm_id: int,
        node_predictions: List[Dict[str, Any]],
        wind_speed: float = 1.5,
        wind_direction: float = 90.0,
        farm_origin_lat: Optional[float] = None,
        farm_origin_lon: Optional[float] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Executes wind-aware source likelihood estimation.
        
        :param farm_id: ID of the farm.
        :param node_predictions: List of dicts containing:
            - node_id: str
            - latitude: float
            - longitude: float
            - is_disease: bool
            - predicted_class: str
            - confidence: float
            - (optional) gas_readings or response_strength
        :param wind_speed: Wind speed in m/s (>= 0.0)
        :param wind_direction: Meteorological wind direction in degrees (0 = North, 90 = East, etc.)
        :param farm_origin_lat: Reference latitude for metric conversion (defaults to farm or first node)
        :param farm_origin_lon: Reference longitude for metric conversion
        :param save_to_db: Whether to persist the localization result to the database
        """
        # 1. Identify triggering nodes and detected disease conditions
        trigger_nodes: List[str] = []
        detected_conditions_set = set()

        for np in node_predictions:
            if np.get("is_disease", False):
                node_id = np.get("node_id")
                if node_id:
                    trigger_nodes.append(node_id)
                cond = np.get("predicted_class")
                if cond and cond not in ("Rice_Healthy", "Jowar_Healthy"):
                    detected_conditions_set.add(cond)

        detected_conditions = sorted(list(detected_conditions_set))

        # If no nodes detected disease, localization is strictly inactive
        if not trigger_nodes:
            return {
                "active": False,
                "message": "All nodes reported healthy baseline; spatial localization inactive.",
                "farm_local": None,
                "geo": None,
                "affected_zone": None,
                "trigger_nodes": [],
                "detected_conditions": [],
                "source_score": 0.0
            }

        # 2. Resolve farm origin GPS coordinates
        origin_lat = farm_origin_lat
        origin_lon = farm_origin_lon

        if origin_lat is None or origin_lon is None:
            if self.farm_repo:
                farm = self.farm_repo.get_by_id(farm_id)
                if farm and farm.latitude is not None and farm.longitude is not None:
                    origin_lat = farm.latitude
                    origin_lon = farm.longitude

        if origin_lat is None or origin_lon is None:
            # Fallback to mean of node coordinates
            valid_nodes = [n for n in node_predictions if n.get("latitude") and n.get("longitude")]
            if valid_nodes:
                origin_lat = sum(n["latitude"] for n in valid_nodes) / len(valid_nodes)
                origin_lon = sum(n["longitude"] for n in valid_nodes) / len(valid_nodes)
            else:
                origin_lat, origin_lon = 16.506174, 80.648015  # Default AP agricultural belt reference

        # 3. Convert all reporting nodes to local metric coordinates (X = East, Y = North in meters)
        metric_nodes = []
        for np in node_predictions:
            n_lat = np.get("latitude")
            n_lon = np.get("longitude")
            if n_lat is None or n_lon is None:
                continue
            x_m, y_m = gps_to_metric(n_lat, n_lon, origin_lat, origin_lon)
            metric_nodes.append({
                "node_id": np.get("node_id"),
                "x": x_m,
                "y": y_m,
                "lat": n_lat,
                "lon": n_lon,
                "is_disease": np.get("is_disease", False),
                "confidence": float(np.get("confidence", 0.5)),
                "predicted_class": np.get("predicted_class", "Healthy"),
                "response_strength": float(np.get("response_strength", 1.0))
            })

        if not metric_nodes:
            # Fallback if no valid node coordinates are present
            return {
                "active": True,
                "farm_local": {"x": 0.0, "y": 0.0},
                "geo": {"latitude": origin_lat, "longitude": origin_lon},
                "affected_zone": {"center_x": 0.0, "center_y": 0.0, "radius_m": 15.0},
                "trigger_nodes": trigger_nodes,
                "detected_conditions": detected_conditions,
                "source_score": 0.5
            }

        # 4. Wind Geometry Transformation
        # Wind direction is meteorological (from which wind blows).
        # Downwind travel angle = (wind_direction + 180) % 360
        downwind_dir_deg = (wind_direction + 180.0) % 360.0
        downwind_rad = math.radians(downwind_dir_deg)

        # Unit vector along downwind travel direction (East = sin, North = cos)
        u_x = math.sin(downwind_rad)
        u_y = math.cos(downwind_rad)

        # Crosswind unit vector (perpendicular to downwind, 90 deg clockwise)
        v_x = math.cos(downwind_rad)
        v_y = -math.sin(downwind_rad)

        effective_wind_speed = max(0.0, float(wind_speed))

        # 5. Define Candidate Search Grid
        all_xs = [n["x"] for n in metric_nodes]
        all_ys = [n["y"] for n in metric_nodes]
        margin = 35.0  # Search margin beyond nodes in meters

        min_x = min(all_xs) - margin
        max_x = max(all_xs) + margin
        min_y = min(all_ys) - margin
        max_y = max(all_ys) + margin

        # Create candidate points with grid resolution ~3.0 meters
        grid_step = 3.0
        cand_xs = []
        curr_x = min_x
        while curr_x <= max_x:
            cand_xs.append(curr_x)
            curr_x += grid_step

        cand_ys = []
        curr_y = min_y
        while curr_y <= max_y:
            cand_ys.append(curr_y)
            curr_y += grid_step

        best_score = -1e9
        best_x = all_xs[0]
        best_y = all_ys[0]

        diseased_nodes = [n for n in metric_nodes if n["is_disease"]]
        healthy_nodes = [n for n in metric_nodes if not n["is_disease"]]

        # 6. Grid Likelihood Evaluation
        for cx in cand_xs:
            for cy in cand_ys:
                # Evaluate influence on diseased nodes
                score = 0.0
                total_disease_weight = 0.0

                for dn in diseased_nodes:
                    dx_vec = dn["x"] - cx
                    dy_vec = dn["y"] - cy
                    dist = math.sqrt(dx_vec * dx_vec + dy_vec * dy_vec)

                    # Project along downwind and crosswind
                    downwind_dist = dx_vec * u_x + dy_vec * u_y
                    crosswind_dist = abs(dx_vec * v_x + dy_vec * v_y)

                    influence = self._calculate_plume_influence(
                        downwind_dist=downwind_dist,
                        crosswind_dist=crosswind_dist,
                        total_dist=dist,
                        wind_speed=effective_wind_speed
                    )

                    weight = dn["confidence"] * dn["response_strength"]
                    score += weight * influence
                    total_disease_weight += weight

                # Penalize candidates that predict heavy plumes on nodes that reported healthy
                if healthy_nodes:
                    for hn in healthy_nodes:
                        dx_vec = hn["x"] - cx
                        dy_vec = hn["y"] - cy
                        dist = math.sqrt(dx_vec * dx_vec + dy_vec * dy_vec)
                        downwind_dist = dx_vec * u_x + dy_vec * u_y
                        crosswind_dist = abs(dx_vec * v_x + dy_vec * v_y)

                        healthy_infl = self._calculate_plume_influence(
                            downwind_dist=downwind_dist,
                            crosswind_dist=crosswind_dist,
                            total_dist=dist,
                            wind_speed=effective_wind_speed
                        )
                        # Penalize candidate if it impinges heavily on a healthy node
                        score -= (hn["confidence"] * 0.45) * healthy_infl

                # Normalize score by disease weights
                if total_disease_weight > 0:
                    normalized_score = score / total_disease_weight
                else:
                    normalized_score = score

                if normalized_score > best_score:
                    best_score = normalized_score
                    best_x = cx
                    best_y = cy

        # 7. Convert best candidate back to GPS coordinates
        estimated_lat, estimated_lon = metric_to_gps(best_x, best_y, origin_lat, origin_lon)

        # Scale source score into a human-readable prototype likelihood [0.30 - 0.96]
        # (Explicitly documented as an empirical likelihood score, not a calibrated probability)
        avg_confidence = sum(d["confidence"] for d in diseased_nodes) / max(len(diseased_nodes), 1)
        clamped_score = max(0.0, min(best_score, 1.0))
        final_source_score = round(0.40 + 0.55 * (clamped_score * 0.6 + avg_confidence * 0.4), 2)

        # 8. Compute Affected Zone Attributes
        # Nearest node to estimated source
        nearest_node = None
        min_node_dist = 1e9
        for n in metric_nodes:
            d = math.sqrt((n["x"] - best_x) ** 2 + (n["y"] - best_y) ** 2)
            if d < min_node_dist:
                min_node_dist = d
                nearest_node = n["node_id"]

        # Single node alert: tighter radius around source (e.g. 5-10m)
        # Multi-node alert: larger radius reflecting plume dispersion
        if len(diseased_nodes) == 1:
            radius_m = round(max(3.5, min(12.0, 5.0 + (1.0 - clamped_score) * 6.0)), 1)
        else:
            radius_m = round(max(6.0, min(25.0, 10.0 + len(diseased_nodes) * 3.5)), 1)

        # Zone severity and inspection priority based on score and affected node count
        if len(diseased_nodes) >= 2 or final_source_score >= 0.85:
            zone_severity = "critical"
            inspection_priority = "immediate"
        elif len(diseased_nodes) == 1 and final_source_score >= 0.65:
            zone_severity = "high"
            inspection_priority = "immediate"
        elif final_source_score >= 0.5:
            zone_severity = "medium"
            inspection_priority = "within_24h"
        else:
            zone_severity = "low"
            inspection_priority = "routine"

        # 8-point circular polygon approximation
        zone_polygon = []
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            poly_x = best_x + radius_m * math.sin(rad)
            poly_y = best_y + radius_m * math.cos(rad)
            p_lat, p_lon = metric_to_gps(poly_x, poly_y, origin_lat, origin_lon)
            zone_polygon.append({
                "latitude": p_lat,
                "longitude": p_lon,
                "x": round(poly_x, 1),
                "y": round(poly_y, 1)
            })

        result_payload = {
            "active": True,
            "farm_local": {
                "x": round(best_x, 1),
                "y": round(best_y, 1)
            },
            "geo": {
                "latitude": estimated_lat,
                "longitude": estimated_lon
            },
            "affected_zone": {
                "center_x": round(best_x, 1),
                "center_y": round(best_y, 1),
                "center_latitude": estimated_lat,
                "center_longitude": estimated_lon,
                "radius_m": radius_m,
                "radius_meters": radius_m,
                "severity": zone_severity,
                "inspection_priority": inspection_priority,
                "nearest_node": nearest_node,
                "polygon": zone_polygon
            },
            "trigger_nodes": trigger_nodes,
            "detected_conditions": detected_conditions,
            "source_score": final_source_score
        }

        # 9. Persist to Database if requested and repository available
        if save_to_db and self.localization_repo:
            primary_trigger = trigger_nodes[0] if trigger_nodes else None
            self.localization_repo.create(
                farm_id=farm_id,
                predicted_source_x=best_x,
                predicted_source_y=best_y,
                estimated_latitude=estimated_lat,
                estimated_longitude=estimated_lon,
                confidence_radius_meters=radius_m,
                source_score=final_source_score,
                trigger_nodes=trigger_nodes,
                detected_conditions=detected_conditions,
                affected_zone=result_payload["affected_zone"],
                trigger_node_id=primary_trigger,
                severity="critical" if len(diseased_nodes) > 1 else "warning",
                status="active"
            )

        return result_payload

    def _calculate_plume_influence(
        self,
        downwind_dist: float,
        crosswind_dist: float,
        total_dist: float,
        wind_speed: float
    ) -> float:
        """
        Calculates relative sensor influence from a candidate VOC source using
        a Gaussian-plume-inspired atmospheric dispersion prototype.
        """
        # Low wind speed (< 0.4 m/s): isotropic diffusion dominates
        if wind_speed < 0.4:
            return 1.0 / (1.0 + (total_dist / 12.0) ** 2)

        # In advective conditions:
        # If node is upwind of source (downwind_dist <= 0):
        if downwind_dist <= 0:
            # Only slight turbulent back-diffusion very close to source
            return math.exp(-(total_dist ** 2) / (2.0 * (5.0 ** 2))) * 0.05

        # Downwind dispersion:
        # Crosswind dispersion parameter grows with downwind distance: sigma_y = sigma_0 + alpha * x
        sigma_y = 4.0 + 0.16 * downwind_dist
        crosswind_decay = math.exp(-(crosswind_dist ** 2) / (2.0 * (sigma_y ** 2)))

        # Downwind concentration attenuation
        downwind_decay = 1.0 / math.sqrt(downwind_dist + 3.0)

        influence = downwind_decay * crosswind_decay
        return min(influence, 1.0)
