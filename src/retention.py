from __future__ import annotations

from typing import List


def retention_recommendations(risk_category: str) -> List[str]:
    if risk_category == "High Risk":
        return ["Offer a loyalty discount", "Trigger a contract upgrade campaign", "Deliver a personalized save offer"]
    if risk_category == "Medium Risk":
        return ["Enroll in a promotional campaign", "Send engagement nudges", "Offer value-added plan comparisons"]
    return ["Reward with loyalty perks", "Upsell premium add-ons selectively", "Encourage referral incentives"]
