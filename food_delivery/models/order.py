from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

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
