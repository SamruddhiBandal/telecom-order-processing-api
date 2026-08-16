from app.database.database import (
    create_order,
    get_all_orders,
    get_order_by_id,
    update_order,
    delete_order,
    update_order_result
)


class OrderRepository:

    # ==========================================
    # CREATE ORDER
    # ==========================================

    def create(self, order_data):

        return create_order(
            order_data
        )


    # ==========================================
    # GET ALL ORDERS
    # ==========================================

    def get_all(self):

        return get_all_orders()


    # ==========================================
    # GET ORDER BY ID
    # ==========================================

    def get_by_id(self, order_id):

        return get_order_by_id(
            order_id
        )


    # ==========================================
    # UPDATE ORDER
    # ==========================================

    def update(
        self,
        order_id,
        order
    ):

        return update_order(
            order_id,
            order
        )


    # ==========================================
    # DELETE ORDER
    # ==========================================

    def delete(self, order_id):

        return delete_order(
            order_id
        )


    # ==========================================
    # UPDATE ORDER PROCESSING RESULT
    # ==========================================

    def update_result(
        self,
        order_id,
        status,
        error_message=None,
        retryable=False
    ):

        return update_order_result(
            order_id=order_id,
            status=status,
            error_message=error_message,
            retryable=retryable
        )