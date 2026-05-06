from fastapi import FastAPI
from services.platform import FoodDeliveryPlatform
from routers import orders, restaurants

# ── Create the FastAPI app ─────────────────────────────────────────
app = FastAPI(
    title="Food Delivery API",
    description="Swiggy Clone built with FastAPI 🚀",
    version="1.0.0",
)

# ── Single shared platform instance (in-memory state) ─────────────
platform = FoodDeliveryPlatform()

# ── Register routers ───────────────────────────────────────────────
app.include_router(orders.router)
app.include_router(restaurants.router)


# ── Root endpoint ──────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"message": "Food Delivery API is running 🚀"}


# ── Partners endpoint ──────────────────────────────────────────────
@app.get("/partners", tags=["Partners"])
async def list_partners():
    """See all delivery partners and their current status."""
    return [
        {
            "partner_id": p.partner_id,
            "name": p.name,
            "area": p.area,
            "type": type(p).__name__,
            "is_available": p.is_available,
            "deliveries_completed": p._deliveries,
        }
        for p in platform._partners
    ]
