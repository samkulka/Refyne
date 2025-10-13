"""
Customer profile models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class RiskLevel(str, Enum):
    """Customer risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EngagementLevel(str, Enum):
    """Customer engagement level"""
    CHAMPION = "champion"
    ACTIVE = "active"
    MODERATE = "moderate"
    AT_RISK = "at_risk"
    DORMANT = "dormant"


class CustomerInsight(BaseModel):
    """Individual insight about a customer"""
    category: str  # e.g., "revenue", "engagement", "risk", "opportunity"
    title: str
    description: str
    severity: str  # "positive", "neutral", "negative"
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")


class CustomerProfile(BaseModel):
    """Complete customer profile with insights"""
    # Basic Info
    customer_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

    # Business Context
    industry: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None

    # Metrics
    account_value: Optional[float] = None
    lifetime_purchases: Optional[float] = None
    total_orders: Optional[int] = None
    average_order_value: Optional[float] = None

    # Engagement
    engagement_score: Optional[int] = Field(None, ge=0, le=100)
    engagement_level: Optional[EngagementLevel] = None
    nps_score: Optional[int] = Field(None, ge=0, le=10)

    # Temporal
    customer_since: Optional[date] = None
    last_purchase_date: Optional[date] = None
    days_since_last_purchase: Optional[int] = None

    # Risk & Opportunity
    churn_risk: Optional[RiskLevel] = None
    expansion_opportunity: Optional[bool] = None

    # Auto-generated insights
    insights: List[CustomerInsight] = []

    # Raw data for reference
    raw_data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "C001",
                "name": "Sarah Mitchell",
                "email": "sarah.mitchell@techcorp.com",
                "company": "TechCorp Solutions",
                "industry": "Technology",
                "account_value": 125000,
                "engagement_score": 95,
                "engagement_level": "champion",
                "insights": [
                    {
                        "category": "revenue",
                        "title": "High-value customer",
                        "description": "Account value of $125,000 places this customer in top 10%",
                        "severity": "positive",
                        "confidence": 0.95
                    }
                ]
            }
        }


class CustomerProfileList(BaseModel):
    """List of customer profiles"""
    total: int
    customers: List[CustomerProfile]
    summary: Optional[Dict[str, Any]] = None
