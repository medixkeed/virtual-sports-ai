from fastapi import APIRouter

from app.schemas import PricingPlanOut

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("", response_model=list[PricingPlanOut])
def pricing():
    return [
        PricingPlanOut(
            id="free",
            name="Free",
            price_label="$0",
            features=[
                "DEMO dashboard access",
                "Limited AI predictions per day",
                "Match analytics (DEMO data)",
            ],
            highlighted=False,
        ),
        PricingPlanOut(
            id="premium",
            name="Premium",
            price_label="Contact admin",
            features=[
                "Unlimited predictions",
                "Priority refresh queue (future)",
                "Advanced analytics (future)",
            ],
            highlighted=True,
        ),
        PricingPlanOut(
            id="team",
            name="Team",
            price_label="Custom",
            features=["Multi-user admin", "API access (future)", "Custom data providers"],
            highlighted=False,
        ),
    ]
