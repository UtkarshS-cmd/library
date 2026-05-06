from fastapi import APIRouter
from schemas.schemas import RestaurantCheckRequest, RestaurantStatusResponse
from services.restaurant import check_all_restaurants

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("/check", response_model=list[RestaurantStatusResponse])
async def check_restaurants(request: RestaurantCheckRequest):
    """Check open/closed status of multiple restaurants concurrently."""
    results = await check_all_restaurants(request.restaurants)
    return results
