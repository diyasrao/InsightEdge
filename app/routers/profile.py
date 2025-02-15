from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
from fastapi.staticfiles import StaticFiles
from bson import ObjectId

from app.schema import schemas
from ..database import databasem
from ..utils import oauth2
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pathlib import Path
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix= "/profile",
                   tags= ["Profile"])


@router.get("/user-profile", status_code= status.HTTP_200_OK)
def user_profile(db: Collection = Depends(databasem.get_db), current_user = Depends(oauth2.get_current_user)):

    user_id = str(current_user["_id"])

    result = {
        "username": current_user["username"],
        "user_id":user_id,
        "fullname": current_user["firstname"] +" "+ current_user["lastname"],
        "first_name":current_user['firstname'],
        "last_name":current_user['lastname'],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
        "profile_status": current_user["public_profile"],
        "about":current_user.get("about",""),
    }

    return result


@router.get("/visiting-user-profile", status_code= status.HTTP_200_OK)
def user_profile(user_id: str, request: Request, db: Collection = Depends(databasem.get_db), current_user = Depends(oauth2.get_current_user)):
    users_collection = db.users

    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    
    result = {
        "user_id":user_id,
        "username": user_doc["username"],
        "fullname": user_doc["firstname"] + " " + user_doc["lastname"],
        "email": user_doc["email"],
        "profile_status": user_doc.get("public_profile", False),
        "about":user_doc.get("about",""),
        "cover_photo": user_doc.get("cover_photo", ""),
        "profile_pic": user_doc.get("profile_pic", "")

    }
    logger.info("returning result")
    logger.info(result)
    return result


@router.put("/profile-status", status_code=status.HTTP_200_OK)
def change_status(
    profile_status: bool, 
    db: Collection = Depends(databasem.get_db), 
    current_user = Depends(oauth2.get_current_user)
):
    users_collection = db.users
    user_doc = users_collection.find_one({"_id": current_user["_id"]})

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not existed")

    user_status = current_user["public_profile"]

    if profile_status == user_status:
        raise HTTPException(
            detail=f"Your profile status is already {profile_status}", 
            status_code=status.HTTP_200_OK
        )
    else:
        new_values = {"$set": {"public_profile": profile_status}}

        result = users_collection.update_one({"_id": current_user["_id"]}, new_values)

        return JSONResponse(content={"detail": f"Status has been changed to {profile_status}"}, status_code=status.HTTP_200_OK)
    
   
@router.post("/new-about")
def create_about(aboutData: schemas.UpdateAbout, db: Collection = Depends(databasem.get_db), current_user = Depends(oauth2.get_current_user)):
    try:
        about=aboutData.new_about
        users = db.users
        user_doc = users.find_one({"_id": current_user["_id"]})

        new_value = {"about": about}
        result = users.update_one({"_id": current_user["_id"]}, {"$set": new_value})

        
        return JSONResponse(content = {"detail": about}, status_code = status.HTTP_200_OK )
    
    except Exception as e:
        logger.error(f"an error occured as {e}")
        raise HTTPException(status_code = 500, detail= str(e))
