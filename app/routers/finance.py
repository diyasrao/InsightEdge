from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from ..utils import oauth2
from ..database import databasem

class FinancialInput(BaseModel):
    household_income: float = Field(..., gt=0)
    debts: float = Field(..., gt=0)
    household_size: int = Field(..., gt=0)
    age: int = Field(..., gt=18)
    occupation: str
    education_level: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

financial_router = APIRouter(
    prefix="/financial",
    tags=["Financial Input"]
)

@financial_router.post("/input", status_code=status.HTTP_201_CREATED)
async def submit_financial_details(
    financial_data: FinancialInput,
    db: Collection = Depends(databasem.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    try:
        financial_collection = db["financial_details"]
        
        financial_record = {
            "user_id": str(current_user["_id"]),
            "household_income": financial_data.household_income,
            "debt": financial_data.debts,
            "household_size": financial_data.household_size,
            "age": financial_data.age,
            "occupation": financial_data.occupation,
            "education_level": financial_data.education_level,
            "created_at": financial_data.created_at
        }
        
        # Insert or update financial details
        financial_collection.update_one(
            {"user_id": str(current_user["_id"])},
            {"$set": financial_record},
            upsert=True
        )
        
        return {"message": "Financial details submitted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting financial details: {str(e)}"
        )
