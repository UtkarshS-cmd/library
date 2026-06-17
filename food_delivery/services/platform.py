import asyncio
from models.partner import DeliveryPartner, BikeDelivery, EVDelivery
from models.order import Order, OrderItem
from services.restaurant import check_restaurant_status

# Custom exceptions stay exactly the same
class DeliveryError(Exception): pass
class RestaurantClosedError(DeliveryError):
    def __init__(self, name: str):
        super().__init__(f"{name} is currently closed.")
class NoDeliveryPartnerError(DeliveryError):
    def __init__(self, area: str):
        super().__init__(f"No delivery partner available in {area}.")

class FoodDeliveryPlatform:
    def __init__(self):
        self._partners: list[DeliveryPartner] = []
        self._orders: list[Order] = []
        self._setup_partners()

    def _setup_partners(self):
        """Pre-load delivery partners on startup."""
        self._partners = [
            BikeDelivery("P001", "Raju",   "Koramangala"),
            BikeDelivery("P002", "Suresh", "Koramangala"),
            EVDelivery(  "P003", "Amara",  "Koramangala"),
        ]

    def get_available_partner(self, area: str) -> DeliveryPartner:
        available = [p for p in self._partners if p.is_available and p.area == area]
        if not available:
            raise NoDeliveryPartnerError(area)
        return min(available, key=lambda p: p._deliveries)

    async def place_order(self, order: Order, distance_km: float) -> dict:
        status = await check_restaurant_status(order.restaurant)
        if not status["is_open"]:
            raise RestaurantClosedError(order.restaurant)

        partner = self.get_available_partner(order.area)
        eta = partner.estimate_time(distance_km)
        fee = partner.delivery_fee(distance_km)
        order.partner = partner.name
        self._orders.append(order)

        asyncio.create_task(partner.pick_up(order.order_id))

        return {
            "order_id": order.order_id,
            "partner": partner.name,
            "partner_type": type(partner).__name__,
            "eta_mins": eta,
            "delivery_fee": fee,
            "food_total": order.food_total,
            "grand_total": order.food_total + fee,
        }
