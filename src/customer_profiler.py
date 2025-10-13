"""
Customer Profile Generator

Analyzes customer CSV data and generates rich profiles with auto-generated insights
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class CustomerProfiler:
    """Generates customer profiles with insights from CSV data"""

    def __init__(self):
        self.customer_id_columns = ['customer_id', 'id', 'customer_number', 'account_id']
        self.name_columns = ['name', 'customer_name', 'full_name', 'contact_name']

    def profile_customers(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate customer profiles from dataframe

        Args:
            df: DataFrame containing customer data

        Returns:
            List of customer profile dictionaries
        """
        profiles = []

        for idx, row in df.iterrows():
            profile = self._build_profile(row, df)
            profiles.append(profile)

        return profiles

    def _build_profile(self, row: pd.Series, df: pd.DataFrame) -> Dict[str, Any]:
        """Build a single customer profile with insights"""

        # Extract basic info
        profile = {
            "customer_id": self._get_field(row, ['customer_id', 'id']),
            "name": self._get_field(row, ['name', 'customer_name']),
            "email": self._get_field(row, ['email', 'email_address']),
            "phone": self._get_field(row, ['phone', 'phone_number', 'mobile']),
            "company": self._get_field(row, ['company', 'organization', 'account_name']),
            "industry": self._get_field(row, ['industry', 'sector']),
            "job_title": self._get_field(row, ['job_title', 'title', 'position']),
            "location": self._get_field(row, ['location', 'city', 'region']),
        }

        # Extract metrics
        account_value = self._get_numeric(row, ['account_value', 'arr', 'contract_value'])
        lifetime_purchases = self._get_numeric(row, ['lifetime_purchases', 'ltv', 'total_revenue'])
        total_orders = self._get_numeric(row, ['total_orders', 'order_count', 'purchases'])
        engagement_score = self._get_numeric(row, ['engagement_score', 'health_score'])
        nps_score = self._get_numeric(row, ['nps_score', 'nps'])
        support_tickets = self._get_numeric(row, ['support_tickets', 'tickets', 'issues'])

        profile.update({
            "account_value": account_value,
            "lifetime_purchases": lifetime_purchases,
            "total_orders": int(total_orders) if total_orders else None,
            "engagement_score": int(engagement_score) if engagement_score else None,
            "nps_score": int(nps_score) if nps_score else None,
        })

        # Calculate derived metrics
        if lifetime_purchases and total_orders:
            profile["average_order_value"] = lifetime_purchases / total_orders

        # Extract dates
        customer_since = self._get_date(row, ['customer_since', 'created_at', 'signup_date'])
        last_purchase = self._get_date(row, ['last_purchase_date', 'last_order_date'])

        profile.update({
            "customer_since": customer_since.isoformat() if customer_since else None,
            "last_purchase_date": last_purchase.isoformat() if last_purchase else None,
        })

        # Calculate days since last purchase
        if last_purchase:
            days_since = (datetime.now().date() - last_purchase).days
            profile["days_since_last_purchase"] = days_since

        # Determine engagement level
        profile["engagement_level"] = self._calculate_engagement_level(
            engagement_score, profile.get("days_since_last_purchase"), nps_score
        )

        # Calculate churn risk
        profile["churn_risk"] = self._calculate_churn_risk(
            engagement_score,
            profile.get("days_since_last_purchase"),
            support_tickets,
            nps_score
        )

        # Generate insights
        profile["insights"] = self._generate_insights(profile, row, df)

        # Store raw data
        profile["raw_data"] = row.to_dict()

        return profile

    def _generate_insights(
        self,
        profile: Dict[str, Any],
        row: pd.Series,
        df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Generate auto insights about the customer"""
        insights = []

        # Revenue insights
        if profile.get("account_value"):
            percentile = self._get_percentile(df, 'account_value', profile["account_value"])
            if percentile >= 90:
                insights.append({
                    "category": "revenue",
                    "title": "Top 10% High-Value Customer",
                    "description": f"Account value of ${profile['account_value']:,.0f} places this customer in the top 10%",
                    "severity": "positive",
                    "confidence": 0.95
                })
            elif percentile >= 75:
                insights.append({
                    "category": "revenue",
                    "title": "Above Average Account Value",
                    "description": f"Account value of ${profile['account_value']:,.0f} is above average",
                    "severity": "positive",
                    "confidence": 0.85
                })

        # Engagement insights
        engagement = profile.get("engagement_score", 0)
        if engagement >= 90:
            insights.append({
                "category": "engagement",
                "title": "Highly Engaged Customer",
                "description": f"Engagement score of {engagement} indicates strong product adoption",
                "severity": "positive",
                "confidence": 0.9
            })
        elif engagement < 70:
            insights.append({
                "category": "engagement",
                "title": "Low Engagement Warning",
                "description": f"Engagement score of {engagement} suggests customer may need attention",
                "severity": "negative",
                "confidence": 0.8
            })

        # Churn risk insights
        if profile.get("churn_risk") == "high":
            reasons = []
            if profile.get("days_since_last_purchase", 0) > 90:
                reasons.append("no recent purchases")
            if engagement < 70:
                reasons.append("low engagement")
            if profile.get("nps_score", 10) < 7:
                reasons.append("low NPS")

            insights.append({
                "category": "risk",
                "title": "High Churn Risk",
                "description": f"Customer shows churn indicators: {', '.join(reasons)}",
                "severity": "negative",
                "confidence": 0.85
            })

        # NPS insights
        nps = profile.get("nps_score")
        if nps is not None:
            if nps >= 9:
                insights.append({
                    "category": "advocacy",
                    "title": "Promoter - Referral Opportunity",
                    "description": f"NPS score of {nps} indicates strong satisfaction. Consider referral program.",
                    "severity": "positive",
                    "confidence": 0.9
                })
            elif nps <= 6:
                insights.append({
                    "category": "satisfaction",
                    "title": "Detractor - Needs Attention",
                    "description": f"NPS score of {nps} indicates dissatisfaction. Immediate outreach recommended.",
                    "severity": "negative",
                    "confidence": 0.9
                })

        # Purchase pattern insights
        if profile.get("average_order_value") and profile.get("total_orders"):
            avg = profile["average_order_value"]
            orders = profile["total_orders"]
            if orders > 20:
                insights.append({
                    "category": "behavior",
                    "title": "Loyal Repeat Customer",
                    "description": f"{orders} orders with ${avg:,.0f} average. Strong loyalty indicator.",
                    "severity": "positive",
                    "confidence": 0.85
                })

        # Tenure insights
        if profile.get("customer_since"):
            since_date = datetime.fromisoformat(profile["customer_since"]).date()
            years = (datetime.now().date() - since_date).days / 365.25
            if years >= 3:
                insights.append({
                    "category": "loyalty",
                    "title": "Long-term Customer",
                    "description": f"Customer for {years:.1f} years. Prioritize retention.",
                    "severity": "positive",
                    "confidence": 0.95
                })

        # Notes/special mentions
        notes = self._get_field(row, ['notes', 'comments', 'description'])
        if notes and isinstance(notes, str):
            if any(word in notes.lower() for word in ['interested', 'expansion', 'upgrade']):
                insights.append({
                    "category": "opportunity",
                    "title": "Expansion Opportunity",
                    "description": f"Notes indicate interest: {notes[:100]}",
                    "severity": "positive",
                    "confidence": 0.7
                })
            if any(word in notes.lower() for word in ['churn', 'cancel', 'competitor', 'at-risk']):
                insights.append({
                    "category": "risk",
                    "title": "Churn Warning in Notes",
                    "description": f"Notes contain risk indicators: {notes[:100]}",
                    "severity": "negative",
                    "confidence": 0.8
                })

        return insights

    def _calculate_engagement_level(
        self,
        engagement_score: Optional[float],
        days_since_purchase: Optional[int],
        nps_score: Optional[int]
    ) -> str:
        """Determine engagement level"""
        if engagement_score is None:
            return "moderate"

        if engagement_score >= 90 and (nps_score or 0) >= 9:
            return "champion"
        elif engagement_score >= 80:
            return "active"
        elif engagement_score >= 60:
            return "moderate"
        elif engagement_score >= 40 or (days_since_purchase or 0) < 60:
            return "at_risk"
        else:
            return "dormant"

    def _calculate_churn_risk(
        self,
        engagement_score: Optional[float],
        days_since_purchase: Optional[int],
        support_tickets: Optional[float],
        nps_score: Optional[int]
    ) -> str:
        """Calculate churn risk level"""
        risk_factors = 0

        if engagement_score is not None and engagement_score < 70:
            risk_factors += 1
        if days_since_purchase is not None and days_since_purchase > 90:
            risk_factors += 1
        if support_tickets is not None and support_tickets > 5:
            risk_factors += 1
        if nps_score is not None and nps_score < 7:
            risk_factors += 1

        if risk_factors >= 3:
            return "high"
        elif risk_factors >= 2:
            return "medium"
        else:
            return "low"

    def _get_field(self, row: pd.Series, possible_names: List[str]) -> Optional[str]:
        """Get field value from row trying multiple column names"""
        for name in possible_names:
            if name in row.index and pd.notna(row[name]):
                return str(row[name])
        return None

    def _get_numeric(self, row: pd.Series, possible_names: List[str]) -> Optional[float]:
        """Get numeric field value"""
        for name in possible_names:
            if name in row.index and pd.notna(row[name]):
                try:
                    return float(row[name])
                except (ValueError, TypeError):
                    continue
        return None

    def _get_date(self, row: pd.Series, possible_names: List[str]) -> Optional[date]:
        """Get date field value"""
        for name in possible_names:
            if name in row.index and pd.notna(row[name]):
                try:
                    if isinstance(row[name], (date, datetime)):
                        return row[name] if isinstance(row[name], date) else row[name].date()
                    return pd.to_datetime(row[name]).date()
                except (ValueError, TypeError):
                    continue
        return None

    def _get_percentile(self, df: pd.DataFrame, column: str, value: float) -> float:
        """Get percentile rank of a value in a column"""
        if column not in df.columns:
            return 50.0

        valid_values = df[column].dropna()
        if len(valid_values) == 0:
            return 50.0

        percentile = (valid_values < value).sum() / len(valid_values) * 100
        return percentile
