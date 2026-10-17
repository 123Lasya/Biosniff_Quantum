from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories.recommendation_repo import RecommendationRepository


RECOMMENDATION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "Bacterial Blight": {
        "disease_type": "Bacterial Blight",
        "title": "Bacterial Leaf Blight (Xanthomonas oryzae pv. oryzae) Treatment Guidance",
        "priority": "critical",
        "severity_rank": 1,
        "recommendation_text": (
            "Copper hydroxide/streptocycline spray, drain excess water, avoid excess nitrogen, clean farm implements."
        ),
        "summary": "Bacterial Leaf Blight signature detected. High transmission risk in standing water or stormy winds.",
        "recommended_action": (
            "1. Apply copper hydroxide/streptocycline spray as targeted foliar application.\n"
            "2. Drain excess stagnant water from the affected field plot to reduce disease spread.\n"
            "3. Avoid excess nitrogen fertilizer application (delay top-dressing).\n"
            "4. Clean and disinfect farm implements before moving between plots."
        ),
        "precautions": (
            "- Do not move equipment across wet infected canopies.\n"
            "- Disinfect footwear and machinery after field entry.\n"
            "- Avoid foliar overhead irrigation."
        ),
        "follow_up_instruction": "Scout for yellow-wavy foliar lesions. Re-verify node gas resistance trends after 48 hours."
    },
    "Brown Spot": {
        "disease_type": "Brown Spot",
        "title": "Brown Spot (Bipolaris oryzae) Treatment Guidance",
        "priority": "high",
        "severity_rank": 2,
        "recommendation_text": (
            "Propiconazole/mancozeb spray, correct soil potassium deficiency, balanced NPK, seed treatment for next season."
        ),
        "summary": "Brown Spot infection signature detected. Commonly associated with nutrient stress or moisture fluctuations.",
        "recommended_action": (
            "1. Apply propiconazole/mancozeb spray to suppress fungal expansion.\n"
            "2. Correct soil potassium deficiency with muriate of potash.\n"
            "3. Ensure balanced NPK nutrient regime to improve plant vigor.\n"
            "4. Perform seed treatment with recommended fungicide for the next crop season."
        ),
        "precautions": (
            "- Prevent soil drought or severe moisture fluctuations.\n"
            "- Avoid prolonged nutrient starvation."
        ),
        "follow_up_instruction": "Inspect leaves for oval brown spots with grey centers and yellow halos. Recheck VOC baseline in 72h."
    },
    "Rice Blast": {
        "disease_type": "Rice Blast",
        "title": "Rice Blast (Magnaporthe oryzae) Immediate Containment Guidance",
        "priority": "critical",
        "severity_rank": 1,
        "recommendation_text": (
            "Tricyclazole/isoprothiolane spray, maintain water level, avoid excess urea, burn infected straw."
        ),
        "summary": "Aggressive Rice Blast fungal spore activity detected. High risk of leaf and neck blast under high humidity.",
        "recommended_action": (
            "1. Apply tricyclazole/isoprothiolane spray immediately.\n"
            "2. Maintain adequate water level in the field (5-7 cm) to mitigate drought-induced blast vulnerability.\n"
            "3. Avoid excess urea application (split nitrogen into smaller doses).\n"
            "4. Burn or safely remove heavily infected crop straw after harvest."
        ),
        "precautions": (
            "- Do not discard infected straw into field bunds or irrigation ditches.\n"
            "- Operators should wear personal protective equipment."
        ),
        "follow_up_instruction": "Scout spindle-shaped lesions with grey centers. Monitor spatial likelihood zone daily."
    },
    "Sheath Blight": {
        "disease_type": "Sheath Blight",
        "title": "Rice Sheath Blight (Rhizoctonia solani) Containment Guidance",
        "priority": "high",
        "severity_rank": 2,
        "recommendation_text": (
            "Hexaconazole/validamycin spray, weed management, avoid dense planting, reduce humidity at base."
        ),
        "summary": "Sheath Blight fungal signature observed from lower canopy humidity and VOC gas array.",
        "recommended_action": (
            "1. Apply hexaconazole/validamycin spray directed towards the base of tillers.\n"
            "2. Perform weed management along field bunds to eliminate alternative host plants.\n"
            "3. Avoid dense planting in subsequent cycles; improve canopy aeration.\n"
            "4. Reduce humidity at the base of plants by managing standing water depth."
        ),
        "precautions": (
            "- Avoid excess nitrogen which promotes thick lush canopy microclimates.\n"
            "- Sterilize field boots when transitioning across zones."
        ),
        "follow_up_instruction": "Check bottom leaf sheaths for greenish-grey water-soaked lesions. Re-assess within 48 hours."
    },
    "Healthy": {
        "disease_type": "Healthy",
        "title": "Optimal Crop Health & Environmental Maintenance Guidance",
        "priority": "preventive",
        "severity_rank": 3,
        "recommendation_text": (
            "Continue routine monitoring, maintain water management, optimal fertilization schedule."
        ),
        "summary": "All sensor nodes reflect healthy crop metabolic baseline. No disease VOC anomalies detected.",
        "recommended_action": (
            "1. Continue routine monitoring across all sensor nodes.\n"
            "2. Maintain recommended water management according to crop growth stage.\n"
            "3. Follow optimal balanced fertilization schedule."
        ),
        "precautions": (
            "- Maintain clean field bunds and check sensor intake vents.\n"
            "- Keep node batteries charged and antennas oriented vertically."
        ),
        "follow_up_instruction": "Automated 24/7 continuous monitoring active. Next cycle evaluates at the top of the hour."
    }
}

# Aliases to map model output classes cleanly
DISEASE_NAME_MAP = {
    "bacterial blight": "Bacterial Blight",
    "bacterial_blight": "Bacterial Blight",
    "rice_bacterial_blight": "Bacterial Blight",
    "rice bacterial blight": "Bacterial Blight",
    "brown spot": "Brown Spot",
    "brown_spot": "Brown Spot",
    "rice_brown_spot": "Brown Spot",
    "rice brown spot": "Brown Spot",
    "rice blast": "Rice Blast",
    "rice_blast": "Rice Blast",
    "blast": "Rice Blast",
    "sheath blight": "Sheath Blight",
    "sheath_blight": "Sheath Blight",
    "rice_sheath_blight": "Sheath Blight",
    "rice sheath blight": "Sheath Blight",
    "healthy": "Healthy",
    "rice_healthy": "Healthy",
    "jowar_healthy": "Healthy",
}


def normalize_disease_name(raw_name: str) -> str:
    cleaned = raw_name.strip().lower().replace("-", "_")
    return DISEASE_NAME_MAP.get(cleaned, raw_name)


class RecommendationService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = RecommendationRepository(db) if db else None

    def generate_recommendations(
        self,
        detected_conditions: List[str],
        farm_id: Optional[int] = None,
        prediction_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates tailored agronomic recommendations:
        - If healthy (or empty): returns Healthy guidance
        - If multiple diseases detected: combines them without dropping any disease,
          prioritizing critical/high severity first.
        - Persists to database with: recommendation_id, farm_id, disease_type, recommendation_text, priority, created_at.
        """
        # Normalize and filter conditions
        normalized_diseases: List[str] = []
        for raw in detected_conditions:
            norm = normalize_disease_name(raw)
            if norm not in ("Healthy",) and norm not in normalized_diseases:
                normalized_diseases.append(norm)

        # Sort diseases by severity rank (critical first, then high)
        def get_rank(d: str) -> int:
            tpl = RECOMMENDATION_TEMPLATES.get(d)
            return tpl.get("severity_rank", 99) if tpl else 99

        normalized_diseases.sort(key=get_rank)

        results: List[Dict[str, Any]] = []

        if not normalized_diseases:
            # Healthy farm guidance
            template = RECOMMENDATION_TEMPLATES["Healthy"]
            db_rec = None
            if self.repo and farm_id is not None:
                db_rec = self.repo.create(
                    farm_id=farm_id,
                    disease_name="Healthy",
                    title=template["title"],
                    details=template["recommendation_text"],
                    action_type="maintenance",
                    urgency="preventive",
                    prediction_id=prediction_id
                )

            rec_obj = {
                "recommendation_id": db_rec.recommendation_id if db_rec else 1,
                "farm_id": farm_id,
                "condition": "Healthy",
                "disease_type": "Healthy",
                "disease_name": "Healthy",
                "priority": template["priority"],
                "recommendation_text": template["recommendation_text"],
                "recommendation": template["recommendation_text"],
                "actionable_advice": template["recommended_action"],
                "treatment": template["recommended_action"],
                "title": template["title"],
                "summary": template["summary"],
                "recommended_action": template["recommended_action"],
                "precautions": template["precautions"],
                "follow_up_instruction": template["follow_up_instruction"],
                "created_at": db_rec.created_at if db_rec else None,
                "disclaimer": "Agricultural prototype guidance for decision-support; consult certified agronomists for regulated treatments."
            }
            results.append(rec_obj)
            return results

        # Process all detected diseases (multi-disease support without dropping any)
        for disease in normalized_diseases:
            template = RECOMMENDATION_TEMPLATES.get(
                disease,
                RECOMMENDATION_TEMPLATES.get("Sheath Blight")
            )

            db_rec = None
            if self.repo and farm_id is not None:
                db_rec = self.repo.create(
                    farm_id=farm_id,
                    disease_name=template["disease_type"],
                    title=template["title"],
                    details=template["recommendation_text"],
                    action_type="treatment",
                    urgency=template["priority"],
                    prediction_id=prediction_id
                )

            rec_obj = {
                "recommendation_id": db_rec.recommendation_id if db_rec else len(results) + 1,
                "farm_id": farm_id,
                "condition": template["disease_type"],
                "disease_type": template["disease_type"],
                "disease_name": template["disease_type"],
                "priority": template["priority"],
                "recommendation_text": template["recommendation_text"],
                "recommendation": template["recommendation_text"],
                "actionable_advice": template["recommended_action"],
                "treatment": template["recommended_action"],
                "title": template["title"],
                "summary": template["summary"],
                "recommended_action": template["recommended_action"],
                "precautions": template["precautions"],
                "follow_up_instruction": template["follow_up_instruction"],
                "created_at": db_rec.created_at if db_rec else None,
                "disclaimer": "Agricultural prototype guidance for decision-support; consult certified agronomists for regulated treatments."
            }
            results.append(rec_obj)

        return results

    def get_farm_recommendations(self, farm_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.repo:
            return []
        recs = self.repo.get_by_farm_id(farm_id=farm_id, limit=limit)
        return [
            {
                "recommendation_id": r.recommendation_id,
                "farm_id": r.farm_id,
                "disease_type": r.disease_name,
                "disease_name": r.disease_name,
                "title": r.title,
                "details": r.details,
                "recommendation_text": r.details,
                "recommendation": r.details,
                "actionable_advice": r.details,
                "treatment": r.details,
                "priority": r.urgency,
                "urgency": r.urgency,
                "action_type": r.action_type,
                "dosage": r.dosage,
                "created_at": r.created_at
            }
            for r in recs
        ]
