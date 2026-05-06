from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Request schemas (what the CLIENT sends IN) ──────────────────────

class OrderItemRequest(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    quantity: int = Field(default=1, ge=1, description="At least 1 item")


class PlaceOrderRequest(BaseModel):
    order_id: str
    customer: str
    restaurant: str
    area: str
    distance_km: float = Field(gt=0, description="Distance must be positive")
    items: list[OrderItemRequest]


class RestaurantCheckRequest(BaseModel):
    restaurants: list[str]


# ── Response schemas (what the SERVER sends OUT) ────────────────────

class OrderResponse(BaseModel):
    order_id: str
    partner: str
    partner_type: str
    eta_mins: int
    delivery_fee: float
    food_total: float
    grand_total: float


class RestaurantStatusResponse(BaseModel):
    name: str
    is_open: bool
    eta_mins: int
