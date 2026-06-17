import asyncio, random
from abc import ABC, abstractmethod

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
    def estimate_time(self, distance_km: float) -> int: ...

    @abstractmethod
    def delivery_fee(self, distance_km: float) -> float: ...

    async def pick_up(self, order_id: str) -> None:
        self._is_available = False
        print(f"  [{self.name}] Picking up order {order_id}...")
        await asyncio.sleep(random.uniform(0.5, 1.5))
        self._deliveries += 1
        self._is_available = True
        print(f"  [{self.name}] Order {order_id} delivered!")

class BikeDelivery(DeliveryPartner):
    SPEED_KM_PER_MIN = 0.5
    def estimate_time(self, distance_km: float) -> int:
        return int(distance_km / self.SPEED_KM_PER_MIN) + 5
    def delivery_fee(self, distance_km: float) -> float:
        return 20 + distance_km * 8

class EVDelivery(DeliveryPartner):
    SPEED_KM_PER_MIN = 0.65
    def estimate_time(self, distance_km: float) -> int:
        return int(distance_km / self.SPEED_KM_PER_MIN) + 3
    def delivery_fee(self, distance_km: float) -> float:
        return 25 + distance_km * 9
