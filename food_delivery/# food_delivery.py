# food_delivery.py — Async Food Delivery Platform
import asyncio, aiohttp, json, random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# ─── Custom Exceptions ─────────────────────────────────────────────
class DeliveryError(Exception): pass

class RestaurantClosedError(DeliveryError):
    def __init__(self, name: str):
        super().__init__(f"{name} is currently closed.")

class ItemUnavailableError(DeliveryError):
    def __init__(self, item: str, restaurant: str):
        super().__init__(f"{item} is not available at {restaurant}.")

class NoDeliveryPartnerError(DeliveryError):
    def __init__(self, area: str):
        super().__init__(f"No delivery partner available in {area}.")

# ─── Abstract Delivery Partner ─────────────────────────────────────
class DeliveryPartner(ABC):
    def __init__(self, partner_id: str, name: str, area: str):
        self.partner_id = partner_id
        self.name = name
        self.area = area
        self._is_available = True
        self._deliveries = 0

    @property
    def is_available(self) -> bool:
        return self._is_available

    @abstractmethod
    def estimate_time(self, distance_km: float) -> int:
        """Return estimated delivery time in minutes."""
        ...

    @abstractmethod
    def delivery_fee(self, distance_km: float) -> float:
        """Return delivery fee in rupees."""
        ...

    async def pick_up(self, order_id: str) -> None:
        """Simulate going to restaurant and picking up order."""
        self._is_available = False
        print(f"  [{self.name}] Picking up order {order_id}...")
        await asyncio.sleep(random.uniform(0.5, 1.5))  # simulate travel
        self._deliveries += 1
        self._is_available = True
        print(f"  [{self.name}] Order {order_id} delivered!")

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.name}, {self.area})"

# ─── Concrete Delivery Partners ────────────────────────────────────
class BikeDelivery(DeliveryPartner):
    """Standard motorbike delivery."""
    SPEED_KM_PER_MIN = 0.5  # average city speed

    def estimate_time(self, distance_km: float) -> int:
        return int(distance_km / self.SPEED_KM_PER_MIN) + 5  # +5 prep time

    def delivery_fee(self, distance_km: float) -> float:
        return 20 + distance_km * 8  # Rs.20 base + Rs.8/km

class EVDelivery(DeliveryPartner):
    """Electric vehicle delivery — faster, slightly higher fee."""
    SPEED_KM_PER_MIN = 0.65

    def estimate_time(self, distance_km: float) -> int:
        return int(distance_km / self.SPEED_KM_PER_MIN) + 3

    def delivery_fee(self, distance_km: float) -> float:
        return 25 + distance_km * 9

# ─── Order and Restaurant ──────────────────────────────────────────
@dataclass
class OrderItem:
    name: str
    price: float
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

@dataclass
class Order:
    order_id: str
    customer: str
    restaurant: str
    area: str
    items: list[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    partner: Optional[str] = None

    @property
    def food_total(self) -> float:
        return sum(i.subtotal for i in self.items)

    def __str__(self) -> str:
        items_str = ", ".join(f"{i.name}x{i.quantity}" for i in self.items)
        return f"Order({self.order_id}: {items_str} | Rs.{self.food_total:.0f})"

# ─── Async Functions ───────────────────────────────────────────────
async def check_restaurant_status(restaurant_name: str) -> dict:
    """Simulates an async call to a restaurant management system."""
    await asyncio.sleep(random.uniform(0.1, 0.3))  # network delay
    # In real code: async with aiohttp.ClientSession() as s: ...
    return {
        "name": restaurant_name,
        "is_open": random.choice([True, True, True, False]),  # 75% chance open
        "eta_mins": random.randint(15, 40)
    }

async def check_all_restaurants(restaurants: list[str]) -> list[dict]:
    """Check status of ALL restaurants concurrently."""
    tasks = [check_restaurant_status(r) for r in restaurants]
    results = await asyncio.gather(*tasks)
    return list(results)

# ─── Generator: Stream orders from a queue ─────────────────────────
def stream_pending_orders(orders: list[Order]):
    """
    Generator that yields orders one at a time.
    In production: this would stream from a Redis queue or database.
    The generator pattern means we do not load all orders into memory.
    """
    for order in orders:
        yield order

# ─── Platform Coordinator ──────────────────────────────────────────
class FoodDeliveryPlatform:
    def __init__(self, name: str):
        self.name = name
        self._partners: list[DeliveryPartner] = []
        self._orders: list[Order] = []

    def add_partner(self, partner: DeliveryPartner) -> None:
        self._partners.append(partner)
        print(f"Partner added: {partner}")

    def get_available_partner(self, area: str) -> DeliveryPartner:
        """Find an available partner in the given area."""
        available = [
            p for p in self._partners
            if p.is_available and p.area == area
        ]
        if not available:
            raise NoDeliveryPartnerError(area)
        return min(available, key=lambda p: p._deliveries)  # load balance

    async def place_order(self, order: Order, distance_km: float) -> dict:
        """
        Async order placement:
        1. Check restaurant is open
        2. Find a delivery partner
        3. Calculate ETA and fee
        4. Dispatch partner (async)
        """
        # Async restaurant check
        status = await check_restaurant_status(order.restaurant)
        if not status["is_open"]:
            raise RestaurantClosedError(order.restaurant)

        # Find partner (polymorphism: works with BikeDelivery or EVDelivery)
        partner = self.get_available_partner(order.area)
        eta = partner.estimate_time(distance_km)
        fee = partner.delivery_fee(distance_km)
        order.partner = partner.name
        self._orders.append(order)

        # Fire and forget the delivery (non-blocking)
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

    async def process_order_queue(self, pending: list[Order], distance_km: float) -> None:
        """Process all pending orders concurrently using a generator."""
        tasks = []
        for order in stream_pending_orders(pending):  # generator
            tasks.append(self.place_order(order, distance_km))
        results = await asyncio.gather(*tasks, return_exceptions=True)

        print("\n=== Order Processing Summary ===")
        for order, result in zip(pending, results):
            if isinstance(result, Exception):
                print(f"  FAILED {order.order_id}: {result}")
            else:
                print(f"  OK {order.order_id}: ETA {result['eta_mins']}min | Rs.{result['grand_total']:.0f}")

# ─── Main demo ─────────────────────────────────────────────────────
async def main():
    platform = FoodDeliveryPlatform("Swiggy Clone")

    # Add delivery partners
    platform.add_partner(BikeDelivery("P001", "Raju",  "Koramangala"))
    platform.add_partner(BikeDelivery("P002", "Suresh", "Koramangala"))
    platform.add_partner(EVDelivery(  "P003", "Amara",  "Koramangala"))

    # Check multiple restaurant statuses concurrently
    print("\n--- Checking Restaurants ---")
    statuses = await check_all_restaurants([
        "Biryani Blues", "Dominos Koramangala", "MTR Restaurant", "Meghana Foods"
    ])
    for s in statuses:
        status_text = "OPEN" if s["is_open"] else "CLOSED"
        print(f"  {s['name']:<25} [{status_text}]")

    # Create orders
    pending_orders = [
        Order("ORD001", "Ayaan",  "Biryani Blues",       "Koramangala",
              [OrderItem("Chicken Biryani", 220), OrderItem("Raita", 40)]),
        Order("ORD002", "Priya",  "Dominos Koramangala", "Koramangala",
              [OrderItem("Farmhouse Pizza", 349), OrderItem("Garlic Bread", 89)]),
        Order("ORD003", "Vikram", "MTR Restaurant",       "Koramangala",
              [OrderItem("Masala Dosa", 120, 2), OrderItem("Filter Coffee", 40, 2)]),
    ]

    # Process all orders concurrently
    print("\n--- Processing Orders ---")
    await platform.process_order_queue(pending_orders, distance_km=3.5)

    # Wait a moment for async deliveries to complete
    await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())