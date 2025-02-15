from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from ..utils import oauth2
from ..database import databasem

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Analytics"]
)

@dashboard_router.get("/income-analysis")
async def get_income_analysis(
    db: Collection = Depends(databasem.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    try:
        financial_collection = db["financial_details"]
        financial_data = financial_collection.find_one({"user_id": str(current_user["_id"])})
        
        if not financial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial details not found"
            )
        
        yearly_income = financial_data["household_income"] * 12
        yearly_debt_payment = calculate_monthly_payment(financial_data["debt"]) * 12
        disposable_income = yearly_income - yearly_debt_payment
        
        return {
            "yearly_income": round(yearly_income, 2),
            "yearly_debt_payment": round(yearly_debt_payment, 2),
            "disposable_income": round(disposable_income, 2)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing income: {str(e)}"
        )

@dashboard_router.get("/debt-breakdown")
async def get_debt_breakdown(
    db: Collection = Depends(databasem.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    try:
        financial_collection = db["financial_details"]
        financial_data = financial_collection.find_one({"user_id": str(current_user["_id"])})
        
        if not financial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial details not found"
            )
        
        monthly_income = financial_data["household_income"]
        monthly_debt_payment = calculate_monthly_payment(financial_data["debt"])
        monthly_disposable_income = monthly_income - monthly_debt_payment
        
        debt_to_income_ratio = (monthly_debt_payment / monthly_income) * 100
        
        return {
            "total_monthly_income": round(monthly_income, 2),
            "total_monthly_debt_payment": round(monthly_debt_payment, 2),
            "monthly_disposable_income": round(monthly_disposable_income, 2),
            "debt_to_income_ratio": round(debt_to_income_ratio, 2),
            "total_debt": round(financial_data["debt"], 2)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting debt breakdown: {str(e)}"
        )

@dashboard_router.get("/government-plans")
async def get_government_plans(
    db: Collection = Depends(databasem.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    try:
        financial_collection = db["financial_details"]
        financial_data = financial_collection.find_one({"user_id": str(current_user["_id"])})
        
        if not financial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial details not found"
            )
        
        yearly_income = financial_data["household_income"] * 12
        household_size = financial_data["household_size"]
        debt_to_income_ratio = (financial_data["debt"] / yearly_income)
        
        plans = [
            {
                "name": "Federal Student Loan Style (Income-Based)",
                "description": "Income-based repayment plan for educational debts",
                "eligibility": yearly_income < 150000 and financial_data["education_level"] == "Bachelor's or higher",
                "benefit": "Reduced monthly payments based on income"
            },
            {
                "name": "Housing Assistance Program",
                "description": "Support for housing-related expenses",
                "eligibility": yearly_income < 80000 and household_size >= 2,
                "benefit": "Housing cost assistance and counseling"
            },
            {
                "name": "Debt Relief Initiative",
                "description": "Government-backed debt consolidation program",
                "eligibility": debt_to_income_ratio > 0.5,
                "benefit": "Debt consolidation with lower interest rates"
            }
        ]
        
        eligible_plans = [plan for plan in plans if plan["eligibility"]]
        
        return {"government_plans": eligible_plans}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching government plans: {str(e)}"
        )

@dashboard_router.get("/investment-plans")
async def get_investment_plans(
    db: Collection = Depends(databasem.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    try:
        financial_collection = db["financial_details"]
        financial_data = financial_collection.find_one({"user_id": str(current_user["_id"])})
        
        if not financial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial details not found"
            )
        
        age = financial_data["age"]
        yearly_income = financial_data["household_income"] * 12
        debt_to_income_ratio = financial_data["debt"] / yearly_income
        monthly_disposable_income = financial_data["household_income"] - calculate_monthly_payment(financial_data["debt"])
        
        # monthly investment
        recommended_investment = monthly_disposable_income * 0.2 
        
        investment_plans = [
            {
                "name": "Mutual Funds Portfolio",
                "risk_level": "Moderate",
                "recommended_allocation": 40 if age > 40 else 60,
                "description": "Diversified mutual funds portfolio with balanced risk",
                "minimum_investment": min(5000, recommended_investment * 12),
                "suggested_monthly_investment": round(recommended_investment * 0.4, 2)
            },
            {
                "name": "Fixed Income Securities",
                "risk_level": "Low",
                "recommended_allocation": 30 if debt_to_income_ratio > 0.4 else 20,
                "description": "Government and corporate bonds for stable returns",
                "minimum_investment": min(1000, recommended_investment * 12),
                "suggested_monthly_investment": round(recommended_investment * 0.3, 2)
            },
            {
                "name": "Index Funds",
                "risk_level": "Moderate-High",
                "recommended_allocation": 30 if age < 35 else 20,
                "description": "Market index tracking funds for long-term growth",
                "minimum_investment": min(3000, recommended_investment * 12),
                "suggested_monthly_investment": round(recommended_investment * 0.3, 2)
            }
        ]
        
        return {
            "investment_plans": investment_plans,
            "risk_profile": {
                "age_factor": "Conservative" if age > 50 else "Aggressive",
                "income_factor": "Stable" if yearly_income > 100000 else "Growing",
                "debt_burden": "High" if debt_to_income_ratio > 0.4 else "Manageable"
            },
            "recommended_monthly_investment": round(recommended_investment, 2)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching investment plans: {str(e)}"
        )


def calculate_monthly_payment(principal: float, annual_interest_rate: float = 5.0, years: int = 5) -> float:

    #5% annual interest rate and 5-year term
    monthly_rate = annual_interest_rate / 12 / 100
    num_payments = years * 12
    
    if monthly_rate == 0:
        return principal / num_payments
    
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return round(monthly_payment, 2)