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
    }

    return result
