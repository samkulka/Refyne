"""
Customer profiling endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import logging

from api.models.customer import CustomerProfile, CustomerProfileList
from api.config import settings
from src.utils.connectors import DataConnector
from src.customer_profiler import CustomerProfiler

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/customers/{file_id}", response_model=CustomerProfileList)
async def get_customer_profiles(file_id: str, limit: int = 100):
    """
    Extract customer profiles from uploaded CSV file

    Args:
        file_id: ID of uploaded file
        limit: Maximum number of customers to return (default 100)

    Returns:
        List of customer profiles with auto-generated insights
    """
    try:
        # Find the file
        file_path = None
        for ext in settings.allowed_extensions:
            candidate = settings.upload_dir / f"{file_id}{ext}"
            if candidate.exists():
                file_path = candidate
                break

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )

        logger.info(f"Generating customer profiles for: {file_id}")

        # Load data
        df = DataConnector.read_file(str(file_path))

        # Limit rows if specified
        if limit and len(df) > limit:
            df = df.head(limit)

        # Generate profiles
        profiler = CustomerProfiler()
        profiles_data = profiler.profile_customers(df)

        # Convert to Pydantic models
        profiles = [CustomerProfile(**p) for p in profiles_data]

        # Generate summary stats
        total_value = sum(p.account_value for p in profiles if p.account_value)
        avg_engagement = sum(p.engagement_score for p in profiles if p.engagement_score) / len([p for p in profiles if p.engagement_score]) if any(p.engagement_score for p in profiles) else 0

        high_risk = len([p for p in profiles if p.churn_risk == "high"])
        champions = len([p for p in profiles if p.engagement_level == "champion"])

        summary = {
            "total_account_value": total_value,
            "average_engagement_score": round(avg_engagement, 1),
            "high_risk_customers": high_risk,
            "champion_customers": champions,
            "engagement_distribution": {
                "champion": len([p for p in profiles if p.engagement_level == "champion"]),
                "active": len([p for p in profiles if p.engagement_level == "active"]),
                "moderate": len([p for p in profiles if p.engagement_level == "moderate"]),
                "at_risk": len([p for p in profiles if p.engagement_level == "at_risk"]),
                "dormant": len([p for p in profiles if p.engagement_level == "dormant"]),
            }
        }

        logger.info(f"Generated {len(profiles)} customer profiles")

        return CustomerProfileList(
            total=len(profiles),
            customers=profiles,
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Customer profiling error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate customer profiles: {str(e)}"
        )


@router.get("/customers/{file_id}/{customer_id}", response_model=CustomerProfile)
async def get_customer_profile(file_id: str, customer_id: str):
    """
    Get a single customer profile by ID

    Args:
        file_id: ID of uploaded file
        customer_id: Customer ID to retrieve

    Returns:
        Single customer profile with insights
    """
    try:
        # Get all profiles
        profiles_response = await get_customer_profiles(file_id, limit=None)

        # Find specific customer
        customer = next(
            (c for c in profiles_response.customers if c.customer_id == customer_id),
            None
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found in file {file_id}"
            )

        return customer

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get customer profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer profile: {str(e)}"
        )
