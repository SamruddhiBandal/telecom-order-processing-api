from fastapi import APIRouter, HTTPException

from app.models.order import (
    Order,
    OrderResponse,
    ErrorResponse
)

from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ==========================================
# DEPENDENCIES
# ==========================================

repository = OrderRepository()

order_service = OrderService(
    repository
)


# ==========================================
# CREATE ORDER
# ==========================================

@router.post(
    "",
    summary="Create a telecom order"
)
def create_order(order: Order):

    result = order_service.create_order(order)

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


# ==========================================
# GET ORDER
# ==========================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Order not found"
        }
    }
)
def get_order(order_id: str):

    order = order_service.get_order(order_id)

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "order": order
    }


# ==========================================
# PROCESS ORDER
# ==========================================

@router.post(
    "/{order_id}/process",
    summary="Process a telecom order",
    description=(
        "Processes an existing telecom order and "
        "updates its status based on the provisioning result."
    ),
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Order not found"
        }
    }
)
def process_single_order(order_id: str):

    result = order_service.process_order(order_id)

    # --------------------------------------
    # ORDER NOT FOUND
    # --------------------------------------

    if result["message"] == "Order not found":

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # --------------------------------------
    # SUCCESS
    # --------------------------------------

    if result["success"]:

        return {
            "message": result["message"],
            "order_id": result["order_id"],
            "status": result["status"],
            "details": result["details"]
        }

    # --------------------------------------
    # PROCESSING FAILED
    # --------------------------------------

    return {
        "message": result["message"],
        "order_id": result["order_id"],
        "status": result["status"],
        "details": result["details"],
        "retryable": result["retryable"]
    }