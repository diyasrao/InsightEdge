from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

class Event(BaseModel):
    user_id: str
    event_type: str
    metadata: Dict[str, Any] = {}

class User(BaseModel):
    user_id: str
    age: int
    gender: str
    location: str
    sign_up_date: datetime

class Metric(BaseModel):
    timestamp: datetime
    daily_active_users: int
    monthly_active_users: int
    # session_duration: float
    retention_rate: float
    num_posts: int
    num_comments: int
    num_likes: int
    # num_shares: int
    # post_reach: int
    # impressions: int
    # engagement_rate: float
    top_performing_posts: List[str]
    new_sign_ups: int
    # user_demographics: Dict[str, Any]
    # referral_sources: Dict[str, int]
    # in_app_purchases: float
    # ad_revenue: float
    # arpu: float
    # app_crashes: int
    # error_rates: float
    # load_times: float
    # performance_metrics: Dict[str, Any]
