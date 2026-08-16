from fastapi import APIRouter, HTTPException

from app.models.order import (
    Order,
    OrderListResponse,
    OrderDetailResponse,
    OrderCreateResponse,
    ErrorResponse
)

from app.services.order_service import OrderService


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ==========================================
# SERVICE
# ==========================================

order_service = OrderService()


# ==========================================
# CONVERT DATABASE ROW TO DICTIONARY
# ==========================================

def convert_order_to_dict(order):

    return {
        "order_id": order[0],
        "customer_id": order[1],
        "service": order[2],
        "speed": order[3],
        "status": order[4],
        "retry_count": order[5],
        "error_message": order[6],
        "retryable": bool(order[7])
    }


# ==========================================
# CREATE ORDER
# ==========================================

@router.post(
    "/",
    status_code=201,
    response_model=OrderCreateResponse,
    summary="Create a new telecom order",
    description="Creates a new telecom service order with NEW status.",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Order already exists"
        }
    }
)
def add_order(order: Order):

    result = order_service.create_order(order)

    if not result["success"]:

        raise HTTPException(
            status_code=409,
            detail=result["message"]
        )

    return {
        "message": result["message"],
        "order": result["order"]
    }


# ==========================================
# GET ALL ORDERS
# FILTERING + PAGINATION
# ==========================================

@router.get(
    "/",
    response_model=OrderListResponse,
    summary="Get all telecom orders",
    description=(
        "Returns telecom orders with optional "
        "status filtering and pagination."
    )
)
def get_orders(
    status: str | None = None,
    limit: int = 10,
    offset: int = 0
):

    return order_service.get_all_orders(
        status=status,
        limit=limit,
        offset=offset
    )


# ==========================================
# GET SINGLE ORDER
# ==========================================

@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    summary="Get an order by ID",
    description="Returns complete information for a specific telecom order.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Order not found"
        }
    }
)
def get_single_order(order_id: str):

    order = order_service.get_order_by_id(
        order_id
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "order": convert_order_to_dict(order)
    }


# ==========================================
# UPDATE ORDER
# ==========================================

@router.put(
    "/{order_id}",
    summary="Update a telecom order",
    description=(
        "Updates the customer, service, or speed "
        "of an existing order."
    ),
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Order could not be updated"
        },
        404: {
            "model": ErrorResponse,
            "description": "Order not found"
        }
    }
)
def update_single_order(
    order_id: str,
    order: Order
):

    result = order_service.update_order(
        order_id,
        order
    )

    if not result["success"]:

        if result["message"] == "Order not found":

            raise HTTPException(
                status_code=404,
                detail=result["message"]
            )

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return {
        "message": result["message"],
        "order": convert_order_to_dict(
            result["order"]
        )
    }


# ==========================================
# DELETE ORDER
# ==========================================

@router.delete(
    "/{order_id}",
    summary="Delete a telecom order",
    description="Deletes an existing telecom order permanently.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Order not found"
        }
    }
)
def delete_single_order(order_id: str):

    result = order_service.delete_order(
        order_id
    )

    if not result["success"]:

        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return {
        "message": result["message"]
    }


# ==========================================
# PROCESS ORDER
# ==========================================

@router.post(
    "/{order_id}/process",
    summary="Process a telecom order",
    description=(
        "Sends the order to the provisioning "
        "service and updates its processing status."
    ),
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Order not found"
        }
    }
)
def process_single_order(order_id: str):

    order_data = order_service.get_order_by_id(
        order_id
    )

    if not order_data:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order = Order(
        order_id=order_data[0],
        customer_id=order_data[1],
        service=order_data[2],
        speed=order_data[3],
        status=order_data[4],
        retry_count=order_data[5],
        error_message=order_data[6],
        retryable=bool(order_data[7])
    )

    # Mark order as PROCESSING
    order_service.repository.update_result(
        order.order_id,
        "PROCESSING"
    )

    # Process order
    response = order_service.process_order(order)

    # SUCCESS
    if response["status"] == "SUCCESS":

        order_service.repository.update_result(
            order.order_id,
            "COMPLETED"
        )

        return {
            "message": "Order processed successfully",
            "order_id": order.order_id,
            "status": "COMPLETED",
            "details": response["message"]
        }

    # FAILURE
    order_service.repository.update_result(
        order.order_id,
        "FAILED",
        response["message"],
        response["retryable"]
    )

    return {
        "message": "Order processing failed",
        "order_id": order.order_id,
        "status": "FAILED",
        "details": response["message"],
        "retryable": response["retryable"]
    }