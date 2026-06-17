from fastapi import APIRouter, HTTPException
from schemas.schemas import PlaceOrderRequest, OrderResponse
from models.order import Order, OrderItem
from services.platform import FoodDeliveryPlatform, RestaurantClosedError, NoDeliveryPartnerError

router = APIRouter(prefix="/orders", tags=["Orders"])

# Shared platform instance — injected via dependency (see main.py)
def get_platform():
    from main import platform
    return platform

@router.post("/", response_model=OrderResponse)
async def place_order(request: PlaceOrderRequest):
    """Place a single order."""

    # Convert Pydantic schema → your internal dataclass
    items = [
        OrderItem(name=i.name, price=i.price, quantity=i.quantity)
        for i in request.items
    ]
    order = Order(
        order_id=request.order_id,
        customer=request.customer,
        restaurant=request.restaurant,
        area=request.area,
        items=items
    )

    try:
        result = await get_platform().place_order(order, request.distance_km)
        return result                          # Pydantic auto-validates response

    except RestaurantClosedError as e:
        raise HTTPException(status_code=503, detail=str(e))  # 503 = service unavailable

    except NoDeliveryPartnerError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/", tags=["Orders"])
async def list_orders():
    """Get all placed orders."""
    platform = get_platform()
    return [
        {
            "order_id": o.order_id,
            "customer": o.customer,
            "restaurant": o.restaurant,
            "food_total": o.food_total,
            "partner": o.partner
        }
        for o in platform._orders
    ]
