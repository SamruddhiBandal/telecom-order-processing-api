import logging


def provision_order(order):

    try:

        logging.info(
            f"Sending order {order.order_id} "
            "for provisioning"
        )

        logging.debug(
            f"Service requested: {order.service}"
        )

        # ==========================================
        # INTERNET SERVICE
        # ==========================================

        if order.service == "Internet":

            response = {
                "status": "SUCCESS",
                "message": "Service provisioned successfully",
                "retryable": False
            }

        # ==========================================
        # UNSUPPORTED SERVICE
        # ==========================================

        else:

            response = {
                "status": "FAILED",
                "message": "Unsupported service",
                "retryable": False
            }


        logging.info(
            f"Provisioning response: {response}"
        )

        return response


    except Exception as error:

        logging.error(
            f"Provisioning error: {error}"
        )

        return {
            "status": "FAILED",
            "message": str(error),
            "retryable": False
        }