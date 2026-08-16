from fastapi import FastAPI

from app.api.orders import router as orders_router

from app.database.database import (
    create_orders_table,
    migrate_database
)


app = FastAPI(
    title="Telecom Order Processing API",
    description="""
    API for managing and processing telecom service orders.

    Features:
    - Create orders
    - View orders
    - Update orders
    - Delete orders
    - Process telecom provisioning orders
    - Filter and paginate orders
    """,
    version="1.0.0",
    contact={
        "name": "Telecom API Support"
    }
)


@app.on_event("startup")
def startup():

    create_orders_table()
    migrate_database()


app.include_router(
    orders_router
)


@app.get(
    "/",
    summary="API Health Check",
    description="Checks whether the Telecom Order Processing API is running."
)
def home():

    return {
        "message": "Telecom Order Processing API is running"
    }