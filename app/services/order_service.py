from app.models.order import Order
from app.services.provisioning import provision_order


class OrderService:

    def __init__(self, repository):
        self.repository = repository

    # ==========================================
    # CREATE ORDER
    # ==========================================

    def create_order(self, order):

        existing_order = self.repository.get_by_id(
            order.order_id
        )

        if existing_order:
            return {
                "success": False,
                "message": "Order already exists"
            }

        self.repository.create(order)

        return {
            "success": True,
            "message": "Order created successfully",
            "order": order.model_dump()
        }

    # ==========================================
    # GET ORDER
    # ==========================================

    def get_order(self, order_id):

        order_data = self.repository.get_by_id(
            order_id
        )

        if not order_data:
            return None

        return Order(
            order_id=order_data[0],
            customer_id=order_data[1],
            service=order_data[2],
            speed=order_data[3],
            status=order_data[4],
            retry_count=order_data[5],
            error_message=order_data[6],
            retryable=bool(order_data[7])
        )

    # ==========================================
    # PROCESS ORDER
    # ==========================================

    def process_order(self, order_id):

        # --------------------------------------
        # 1. GET ORDER
        # --------------------------------------

        order = self.get_order(order_id)

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        # --------------------------------------
        # 2. UPDATE STATUS TO PROCESSING
        # --------------------------------------

        self.repository.update_result(
            order_id,
            "PROCESSING"
        )

        # Keep local object status updated
        order.status = "PROCESSING"

        # --------------------------------------
        # 3. CALL PROVISIONING SERVICE
        # --------------------------------------

        response = provision_order(order)

        # --------------------------------------
        # 4. SUCCESS
        # --------------------------------------

        if response.get("status") == "SUCCESS":

            self.repository.update_result(
                order_id,
                "COMPLETED"
            )

            return {
                "success": True,
                "message": "Order processed successfully",
                "order_id": order_id,
                "status": "COMPLETED",
                "details": response.get(
                    "message",
                    "Service provisioned successfully"
                )
            }

        # --------------------------------------
        # 5. FAILURE
        # --------------------------------------

        error_message = response.get(
            "message",
            "Provisioning failed"
        )

        retryable = response.get(
            "retryable",
            False
        )

        self.repository.update_result(
            order_id,
            "FAILED",
            error_message,
            retryable
        )

        return {
            "success": False,
            "message": "Order processing failed",
            "order_id": order_id,
            "status": "FAILED",
            "details": error_message,
            "retryable": retryable
        }