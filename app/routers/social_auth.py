import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Collection
from app.config import settings
from app.database import databasem
from app.schema.schemas import SocialSignupResponse
from app.utils import oauth2

router = APIRouter(tags=["Social Authentication"])

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID

@router.post("/auth/google")
async def google_auth(
    user_data: dict, 
    db: Collection = Depends(databasem.get_db)
):
    try:
        users_collection = db["users"]

        # Check if user exists by email
        user = users_collection.find_one({"email": user_data['email']})

        if not user:
            # Return user data to frontend for registration
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "detail": "Account not found. Please register first.",
                    "userData": {
                        "email": user_data['email'],
                        "firstname": user_data.get('firstname', ''),
                        "lastname": user_data.get('lastname', ''),
                        "google_id": user_data['google_id'],
                        "profile_photo": user_data.get('profile_photo', '')
                    }
                }
            )

        user_id = str(user["_id"])

        # Update existing user's Google info
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "google_id": user_data['google_id'],
                "profile_photo": user_data.get('profile_photo', user.get('profile_photo', '')),
                "auth_provider": "google"
            }}
        )

        # Create tokens
        access_token = oauth2.create_access_token(data={"sub": user_id})
        refresh_token = oauth2.create_refresh_token(data={"sub": user_id})

        # Store refresh token
        db["refresh_tokens"].insert_one({
            "user_id": user_id,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow()
        })

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }

    except Exception as e:
        logging.error(f"Error in google_auth: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

