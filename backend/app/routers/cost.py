from fastapi import APIRouter
from .. import services
from ..schemas.cost import CostSummary

router = APIRouter(prefix="/api", tags=["成本"])

@router.get("/cost", response_model=CostSummary)
def cost():
    return services.get_cost_summary()