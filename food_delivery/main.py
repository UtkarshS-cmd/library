from fastapi import FastAPI
from services.platform import FoodDeliveryPlatform
from routers import orders, restaurants

# Create the app
app = FastAPI(
    title="Food Delivery API",
    description="Swiggy Clone built with FastAPI",
    version="1.0.0"
)

# Single shared platform instance (acts as in-memory state)
platform = FoodDeliveryPlatform()

# Register routers
app.include_router(orders.router)
app.include_router(restaurants.router)

@app.get("/")
async def root():
    return {"message": "Food Delivery API is running 🚀"}

@app.get("/partners")
async def list_partners():
    """See all delivery partners and their status."""
    return [
        {
            "name": p.name,
            "area": p.area,
            "type": type(p).__name__,
            "is_available": p.is_available,
            "deliveries": p._deliveries
        }
        for p in platform._partners
    ]

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    
    # Automatically open the browser to localhost!
    webbrowser.open("http://127.0.0.1:8000/docs")
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
