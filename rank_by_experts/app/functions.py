import random
import json
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, PairwiseComparisonSimple, PairwiseComparisonMulti, ResponseSimple, ResponseMulti, Power


def get_user_score(user: User, db: Session):
    """Retrieve user annotation counts."""
    with SessionLocal() as db:
        simple_annotations = db.query(PairwiseComparisonSimple).filter(PairwiseComparisonSimple.user_id == user.id).count()
        multi_annotations = db.query(PairwiseComparisonMulti).filter(PairwiseComparisonMulti.user_id == user.id).count()
    return {
        "simple": simple_annotations,
        "multi": multi_annotations,
        "total": simple_annotations + multi_annotations,
    }


def get_response_obj_simple(response: ResponseSimple):
    """Format a simple response object."""
    return {
        "id": response.id,
        "participant_name": response.participant_name,
        "map_name": response.map_name,
        "player_name": Power[response.player_name],
        "stance": json.loads(response.stance.replace("'", "\"")),
        "orders": response.orders_str,
        "map": response.map_url,
    }


def get_response_obj_multi(response: ResponseMulti):
    """Format a multi-response object."""
    return {
        "id": response.id,
        "participant_name": response.participant_name,
        "map_name": response.map_name,
        "player_name": Power[response.player_name],
        "stance": json.loads(response.stance.replace("'", "\"")),
        "orders": {
            0: response.orders0_str,
            1: response.orders1_str,
        },
        "map": {
            0: response.map_url0,
            1: response.map_url1,
        },
    }
