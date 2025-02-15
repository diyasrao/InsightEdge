from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from models import Event, User, Metric
from datetime import datetime, timedelta
from typing import List

app = FastAPI()

# MongoDB client setup
client = MongoClient("mongodb://localhost:27017/")
db = client['analytics_db']
events_collection = db['events']
users_collection = db['users']
metrics_collection = db['metrics']

@app.post("/log_event")
async def log_event(event: Event):
    event_data = event.dict()
    event_data["event_time"] = datetime.utcnow()
    events_collection.insert_one(event_data)
    return {"success": True}

@app.post("/log_user")
async def log_user(user: User):
    user_data = user.dict()
    users_collection.insert_one(user_data)
    return {"success": True}

@app.get("/metrics")
async def get_metrics():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = today.replace(day=1)
    one_week_ago = today - timedelta(days=7)

    # Calculate DAU
    dau = len(events_collection.distinct("user_id", {"event_time": {"$gte": today}}))

    # Calculate MAU
    mau = len(events_collection.distinct("user_id", {"event_time": {"$gte": start_of_month}}))

    # Calculate session duration adjust based on your actual event structure)
    session_durations = events_collection.aggregate([
        {"$group": {"_id": "$user_id", "total_duration": {"$sum": "$metadata.session_duration"}}}
    ])
    session_duration = sum([doc["total_duration"] for doc in session_durations])

    # Calculate retention rate adjust based on your actual user structure)
    new_users = users_collection.find({"sign_up_date": {"$gte": one_week_ago}})
    new_user_ids = [user["user_id"] for user in new_users]
    retained_users = events_collection.distinct("user_id", {"user_id": {"$in": new_user_ids}})
    retention_rate = len(retained_users) / len(new_user_ids) if new_user_ids else 0

    # Number of posts, comments, likes, and shares
    num_posts = events_collection.count_documents({"event_type": "post_created"})
    num_comments = events_collection.count_documents({"event_type": "post_commented"})
    num_likes = events_collection.count_documents({"event_type": "post_liked"})
    num_shares = events_collection.count_documents({"event_type": "post_shared"})

    # Content Performance Metrics
    post_reach = events_collection.count_documents({"event_type": {"$in": ["post_viewed", "post_liked", "post_shared"]}})
    impressions = events_collection.count_documents({"event_type": "post_viewed"})
    engagement_rate = (num_likes + num_comments + num_shares) / impressions if impressions > 0 else 0

    top_performing_posts = events_collection.aggregate([
        {"$match": {"event_type": {"$in": ["post_liked", "post_commented", "post_shared"]}}},
        {"$group": {"_id": "$metadata.post_id", "engagement": {"$sum": 1}}},
        {"$sort": {"engagement": -1}},
        {"$limit": 5}
    ])
    top_performing_posts = [post["_id"] for post in top_performing_posts]

    # User Growth Metrics
    new_sign_ups = users_collection.count_documents({"sign_up_date": {"$gte": today}})
    user_demographics = users_collection.aggregate([
        {"$group": {"_id": {"age": "$age", "gender": "$gender", "location": "$location"}, "count": {"$sum": 1}}}
    ])
    user_demographics = {str(demo["_id"]): demo["count"] for demo in user_demographics}

    referral_sources = events_collection.aggregate([
        {"$match": {"event_type": "user_referred"}},
        {"$group": {"_id": "$metadata.source", "count": {"$sum": 1}}}
    ])
    referral_sources = {source["_id"]: source["count"] for source in referral_sources}

    # Monetization Metrics
    in_app_purchases = events_collection.aggregate([
        {"$match": {"event_type": "purchase_made"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$metadata.amount"}}}
    ]).next()["total_revenue"]

    ad_revenue = events_collection.aggregate([
        {"$match": {"event_type": "ad_viewed"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$metadata.revenue"}}}
    ]).next()["total_revenue"]

    arpu = (in_app_purchases + ad_revenue) / mau if mau > 0 else 0

    # Technical Metrics
    app_crashes = events_collection.count_documents({"event_type": "app_crash"})
    error_rates = events_collection.count_documents({"event_type": "error_occurred"}) / events_collection.count_documents({}) if events_collection.count_documents({}) > 0 else 0
    load_times = events_collection.aggregate([
        {"$match": {"event_type": "page_load"}},
        {"$group": {"_id": None, "average_load_time": {"$avg": "$metadata.load_time"}}}
    ]).next()["average_load_time"]

    performance_metrics = {
        "app_crashes": app_crashes,
        "error_rates": error_rates,
        "load_times": load_times
    }

    metrics = Metric(
        timestamp=datetime.utcnow(),
        daily_active_users=dau,
        monthly_active_users=mau,
        session_duration=session_duration,
        retention_rate=retention_rate,
        num_posts=num_posts,
        num_comments=num_comments,
        num_likes=num_likes,
        num_shares=num_shares,
        post_reach=post_reach,
        impressions=impressions,
        engagement_rate=engagement_rate,
        top_performing_posts=top_performing_posts,
        new_sign_ups=new_sign_ups,
        user_demographics=user_demographics,
        referral_sources=referral_sources,
        in_app_purchases=in_app_purchases,
        ad_revenue=ad_revenue,
        arpu=arpu,
        app_crashes=app_crashes,
        error_rates=error_rates,
        load_times=load_times,
        performance_metrics=performance_metrics
    )

    metrics_collection.insert_one(metrics.dict())

    return metrics.dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
