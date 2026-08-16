from pydantic import BaseModel, Field, field_validator


# ==========================================
# REQUEST MODEL
# ==========================================

class Order(BaseModel):

    order_id: str = Field(
        min_length=1,
        max_length=50
    )

    customer_id: str = Field(
        min_length=1,
        max_length=50
    )

    service: str = Field(
        min_length=1
    )

    speed: str = Field(
        min_length=1
    )

    status: str = "NEW"

    retry_count: int = Field(
        default=0,
        ge=0
    )

    error_message: str | None = None

    retryable: bool = False

    @field_validator(
        "order_id",
        "customer_id",
        "service",
        "speed"
    )
    @classmethod
    def validate_not_empty(cls, value):

        if not value.strip():
            raise ValueError(
                "Value cannot be empty"
            )

        return value.strip()

    @field_validator("service")
    @classmethod
    def validate_service(cls, value):

        allowed_services = [
            "Internet",
            "Timeout"
        ]

        if value not in allowed_services:
            raise ValueError(
                "Service must be one of: "
                + ", ".join(allowed_services)
            )

        return value


# ==========================================
# SINGLE ORDER RESPONSE
# ==========================================

class OrderResponse(BaseModel):

    order_id: str
    customer_id: str
    service: str
    speed: str
    status: str
    retry_count: int
    error_message: str | None = None
    retryable: bool


# ==========================================
# CREATE ORDER RESPONSE
# ==========================================

class OrderCreateResponse(BaseModel):

    message: str
    order: OrderResponse


# ==========================================
# GET SINGLE ORDER RESPONSE
# ==========================================

class OrderDetailResponse(BaseModel):

    order: OrderResponse


# ==========================================
# GET ALL ORDERS RESPONSE
# ==========================================

class OrderListResponse(BaseModel):

    total_orders: int
    orders: list[OrderResponse]

# ==========================================
# ERROR RESPONSE MODEL
# ==========================================

class ErrorResponse(BaseModel):

    detail: str