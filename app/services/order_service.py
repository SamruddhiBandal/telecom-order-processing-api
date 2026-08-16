from app.repositories.order_repository import OrderRepository
from app.services.provisioning import provision_order


class OrderService:

    def __init__(self):

        self.repository = OrderRepository()


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
                "message": (
                    f"Order {order.order_id} already exists"
                )
            }

        self.repository.create(
            order.model_dump()
        )

        return {
            "success": True,
            "message": "Order created successfully",
            "order": order.model_dump()
        }


    # ==========================================
    # GET ALL ORDERS
    # ==========================================

    def get_all_orders(
        self,
        status=None,
        limit=10,
        offset=0
    ):

        orders = self.repository.get_all()

        orders_list = []

        for order in orders:

            order_dict = {
                "order_id": order[0],
                "customer_id": order[1],
                "service": order[2],
                "speed": order[3],
                "status": order[4],
                "retry_count": order[5],
                "error_message": order[6],
                "retryable": bool(order[7])
            }

            # Filter by status
            if status:

                if (
                    order_dict["status"].upper()
                    != status.upper()
                ):
                    continue

            orders_list.append(
                order_dict
            )

        # Pagination
        paginated_orders = orders_list[
            offset: offset + limit
        ]

        return {
            "total_orders": len(orders_list),
            "orders": paginated_orders
        }


    # ==========================================
    # GET ORDER BY ID
    # ==========================================

    def get_order_by_id(self, order_id):

        return self.repository.get_by_id(
            order_id
        )


    # ==========================================
    # UPDATE ORDER
    # ==========================================

    def update_order(
        self,
        order_id,
        order
    ):

        existing_order = self.repository.get_by_id(
            order_id
        )

        if not existing_order:

            return {
                "success": False,
                "message": "Order not found"
            }

        rows_updated = self.repository.update(
            order_id,
            order
        )

        if rows_updated == 0:

            return {
                "success": False,
                "message": "Order could not be updated"
            }

        updated_order = self.repository.get_by_id(
            order_id
        )

        return {
            "success": True,
            "message": "Order updated successfully",
            "order": updated_order
        }


    # ==========================================
    # DELETE ORDER
    # ==========================================

    def delete_order(self, order_id):

        existing_order = self.repository.get_by_id(
            order_id
        )

        if not existing_order:

            return {
                "success": False,
                "message": "Order not found"
            }

        self.repository.delete(
            order_id
        )

        return {
            "success": True,
            "message": (
                f"Order {order_id} "
                "deleted successfully"
            )
        }


    # ==========================================
    # PROCESS ORDER
    # ==========================================

    def process_order(self, order):

        # IMPORTANT:
        # Pass the Order object directly.
        # provisioning.py uses:
        # order.order_id
        # order.service

        response = provision_order(
            order
        )

        # SUCCESS
        if response["status"] == "SUCCESS":

            return {
                "status": "SUCCESS",
                "message": response["message"],
                "retryable": False
            }

        # FAILURE
        return {
            "status": "FAILED",
            "message": response["message"],
            "retryable": response.get(
                "retryable",
                False
            )
        }