import asyncio
import random


async def check_restaurant_status(restaurant_name: str) -> dict:
    """Simulates an async call to a restaurant management system."""
    await asyncio.sleep(random.uniform(0.1, 0.3))  # network delay
    return {
        "name": restaurant_name,
        "is_open": random.choice([True, True, True, False]),  # 75% chance open
        "eta_mins": random.randint(15, 40),
    }


async def check_all_restaurants(restaurants: list[str]) -> list[dict]:
    """Check status of ALL restaurants concurrently."""
    tasks = [check_restaurant_status(r) for r in restaurants]
    results = await asyncio.gather(*tasks)
    return list(results)
