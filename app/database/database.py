import sqlite3

from config import DATABASE_NAME
from app.logger import get_logger

logger = get_logger(__name__)


def get_connection():

    return sqlite3.connect(DATABASE_NAME)


def create_orders_table():

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                service TEXT NOT NULL,
                speed TEXT,
                status TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                retryable INTEGER DEFAULT 0
            )
        """)

        connection.commit()

        logger.info(
            "Orders table checked/created successfully."
        )

    except sqlite3.Error:

        logger.exception(
            "Error while creating orders table."
        )

    finally:

        if "connection" in locals():
            connection.close()


def migrate_database():

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        columns_to_add = [

            (
                "retry_count",
                "INTEGER DEFAULT 0"
            ),

            (
                "error_message",
                "TEXT"
            ),

            (
                "retryable",
                "INTEGER DEFAULT 0"
            )

        ]

        for column_name, column_type in columns_to_add:

            try:

                cursor.execute(
                    f"""
                    ALTER TABLE orders
                    ADD COLUMN {column_name} {column_type}
                    """
                )

                logger.info(
                    f"Added column: {column_name}"
                )

            except sqlite3.OperationalError:

                logger.debug(
                    f"Column already exists: "
                    f"{column_name}"
                )

        connection.commit()

    except sqlite3.Error:

        logger.exception(
            "Database migration error."
        )

    finally:

        if connection:
            connection.close()


def create_order(order):

    connection = None

    try:

        logger.info(
            f"Creating order: "
            f"{order['order_id']}"
        )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO orders (
                order_id,
                customer_id,
                service,
                speed,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            order["order_id"],
            order["customer_id"],
            order["service"],
            order["speed"],
            order["status"]
        ))

        connection.commit()

        print(
            f"Order {order['order_id']} "
            "created successfully."
        )

        logger.info(
            f"Order created successfully: "
            f"{order['order_id']}"
        )

    except sqlite3.IntegrityError:

        print(
            f"Order {order['order_id']} "
            "already exists."
        )

        logger.warning(
            f"Duplicate order detected: "
            f"{order['order_id']}"
        )

    except sqlite3.Error:

        logger.exception(
            f"Database error while creating "
            f"order {order.get('order_id')}"
        )

    finally:

        if connection:
            connection.close()


def get_new_orders():

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE status = 'NEW'
        """)

        orders = cursor.fetchall()

        logger.debug(
            f"Found {len(orders)} NEW orders."
        )

        return orders

    except sqlite3.Error:

        logger.exception(
            "Error while getting NEW orders."
        )

        return []

    finally:

        if connection:
            connection.close()


def get_retryable_failed_orders(max_retries):

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE status = 'FAILED'
            AND retryable = 1
            AND retry_count < ?
        """, (max_retries,))

        orders = cursor.fetchall()

        logger.debug(
            f"Found {len(orders)} retryable "
            "failed orders."
        )

        return orders

    except sqlite3.Error:

        logger.exception(
            "Error while getting retryable "
            "failed orders."
        )

        return []

    finally:

        if connection:
            connection.close()


def update_order_result(
    order_id,
    status,
    error_message=None,
    retryable=False
):

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE orders
            SET
                status = ?,
                error_message = ?,
                retryable = ?
            WHERE order_id = ?
        """, (
            status,
            error_message,
            int(retryable),
            order_id
        ))

        connection.commit()

        logger.info(
            f"Order {order_id} updated. "
            f"Status: {status}, "
            f"Retryable: {retryable}"
        )

    except sqlite3.Error:

        logger.exception(
            f"Error updating order: {order_id}"
        )

    finally:

        if connection:
            connection.close()


def increment_retry_count(order_id):

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE orders
            SET retry_count = retry_count + 1
            WHERE order_id = ?
        """, (order_id,))

        connection.commit()

        logger.info(
            f"Retry count increased for "
            f"order: {order_id}"
        )

    except sqlite3.Error:

        logger.exception(
            f"Error updating retry count for "
            f"order: {order_id}"
        )

    finally:

        if connection:
            connection.close()


def get_order_by_id(order_id):

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE order_id = ?
        """, (order_id,))

        order = cursor.fetchone()

        logger.debug(
            f"Order lookup completed: "
            f"{order_id}"
        )

        return order

    except sqlite3.Error:

        logger.exception(
            f"Error getting order: {order_id}"
        )

        return None

    finally:

        if connection:
            connection.close()


def get_all_orders():

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM orders
        """)

        orders = cursor.fetchall()

        logger.debug(
            f"Retrieved {len(orders)} "
            "total orders."
        )

        return orders

    except sqlite3.Error:

        logger.exception(
            "Error getting all orders."
        )

        return []

    finally:

        if connection:
            connection.close()

def update_order(order_id, order_data):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE orders
        SET customer_id = ?,
            service = ?,
            speed = ?
        WHERE order_id = ?
        """,
        (
            order_data.customer_id,
            order_data.service,
            order_data.speed,
            order_id
        )
    )

    connection.commit()

    rows_updated = cursor.rowcount

    connection.close()

    return rows_updated


def delete_order(order_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM orders
        WHERE order_id = ?
        """,
        (order_id,)
    )

    connection.commit()

    rows_deleted = cursor.rowcount

    connection.close()

    return rows_deleted