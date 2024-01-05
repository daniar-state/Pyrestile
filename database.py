# Importing libraries
from sqlalchemy import select, update, delete, func

# Importing modules
from models import BaseOrderVP, BaseOrderMG, BaseOrderJM, create_base_tables, database

# Creating class for working with database
class DatabaseManager:
    """
    This class provides methods to manage database operations such as connecting to the database,
    creating tables, and performing CRUD operations for different types of orders.
    """
    
    #! Creating a connection to the database
    async def connect_db(self):
        """
        Connect to the database and ensure that all tables exist.
        """
        await database.connect()
        await self.ensure_tables_exist()
    
    #! Closing a connection to the database
    async def close_db(self):
        """
        Disconnect from the database.
        """
        await database.disconnect()
    
    #! Creating tables if they don't exist
    async def ensure_tables_exist(self):
        """
        Ensure that tables for BaseOrderVP, BaseOrderMG, and BaseOrderJM exist in the database.
        """
        await self._ensure_table_exists(BaseOrderVP.__tablename__)
        await self._ensure_table_exists(BaseOrderMG.__tablename__)
        await self._ensure_table_exists(BaseOrderJM.__tablename__)
    
    #! Creating a table if it doesn't exist
    async def _ensure_table_exists(self, table_name):
        """
        Check if a table exists in the database and create it if it does not.

        :param str table_name: Name of the table to check and create if necessary.
        """
        query = f"SELECT to_regclass('{table_name}')"
        result = await database.execute(query)
        if result is None:
            create_base_tables()
    
    #! Creating a new order in the database for the VP service
    async def createOrderVP(self, user_id, zone_id, quantity, price, product, api_name, order_id, email_user, status, order_details):
        """
        Create a new order for the VP service in the database.

        :param int user_id: ID of the user creating the order.
        :param int zone_id: ID of the zone associated with the order.
        :param int quantity: Quantity of items in the order.
        :param float price: Total price of the order.
        :param str product: Name of the product being ordered.
        :param str api_name: Name of the API used for the order.
        :param str order_id: ID of the order.
        :param str email_user: Email of the user creating the order.
        :param str status: Status of the order.
        :param str order_details: Additional details about the order.
        """
        query = BaseOrderVP.__table__.insert().values(
            user_id=user_id,
            zone_id=zone_id,
            quantity=quantity,
            price=price,
            product=product,
            api_name=api_name,
            order_id=order_id,
            email_user=email_user,
            status=status,
            order_details=order_details,
        )
        await database.execute(query)
    
    #! Receive records of all orders
    async def getAllOrdersVP(self):
        """
        Retrieve records of all VP service orders from the database.

        :return: A list of all VP service orders.
        """
        query = select([BaseOrderVP])
        return await database.fetch_all(query)
    
    #! Receive records of all orders by order_id
    async def getOrderIdVP(self, order_id):
        """
        Retrieve a VP service order from the database by its order_id.

        :param str order_id: ID of the order to retrieve.
        :return: The order matching the given order_id or None if not found.
        """
        query = select([BaseOrderVP]).where(BaseOrderVP.order_id == order_id)
        return await database.fetch_one(query)
    
    #! Receive records of all orders by status
    async def getOrderStatusVP(self, status):
        """
        Retrieve VP service orders from the database with a specific status.

        :param str status: Status of the orders to retrieve.
        :return: A list of orders with the given status.
        """
        query = select([BaseOrderVP]).where(BaseOrderVP.status == status)
        return await database.fetch_all(query)
    
    #! Updating order data for the VP
    async def updateOrderVP(self, order_id, status=None, new_order_details=None):
        """
        Update a VP service order in the database with new status and/or order details.

        :param str order_id: ID of the order to update.
        :param str status: New status to set for the order. If None, the status is not updated.
        :param str new_order_details: New order details to set for the order. If None, the order details are not updated.
        :return: The updated order object.
        """
        query = (
            update(BaseOrderVP)
            .where(BaseOrderVP.order_id == order_id)
            .values(status=status if status is not None else BaseOrderVP.status, order_details=new_order_details if new_order_details is not None else BaseOrderVP.order_details)
            .returning(BaseOrderVP)
        )
        return await database.execute(query)
    
    #! Delete order data for the VP
    async def deleteOrderVP(self, order_id):
        """
        Delete a VP service order from the database by its order_id.

        :param str order_id: ID of the order to delete.
        :return: The result of the delete operation.
        """
        query = delete(BaseOrderVP).where(BaseOrderVP.order_id == order_id)
        return await database.execute(query)
    
    #! Creating a new order in the database for the MG service
    async def createOrderMG(self, user_id, zone_id, quantity, price, product, api_name, order_id, email_user, status, order_details):
        """
        Create a new order for the MG service in the database.

        :param int user_id: ID of the user creating the order.
        :param int zone_id: ID of the zone associated with the order.
        :param int quantity: Quantity of items in the order.
        :param float price: Total price of the order.
        :param str product: Name of the product being ordered.
        :param str api_name: Name of the API used for the order.
        :param str order_id: ID of the order.
        :param str email_user: Email of the user creating the order.
        :param str status: Status of the order.
        :param str order_details: Additional details about the order.
        """
        query = BaseOrderMG.__table__.insert().values(
            user_id=user_id,
            zone_id=zone_id,
            quantity=quantity,
            price=price,
            product=product,
            api_name=api_name,
            order_id=order_id,
            email_user=email_user,
            status=status,
            order_details=order_details,
        )
        await database.execute(query)
    
    #! Receive records of all orders
    async def getAllOrdersMG(self):
        """
        Retrieve records of all MG service orders from the database.

        :return: A list of all MG service orders.
        """
        query = select([BaseOrderMG])
        return await database.fetch_all(query)
    
    #! Receive records of all orders by order_id
    async def getOrderIdMG(self, order_id):
        """
        Retrieve an MG service order from the database by its order_id.

        :param str order_id: ID of the order to retrieve.
        :return: The order matching the given order_id or None if not found.
        """
        query = select([BaseOrderMG]).where(BaseOrderMG.order_id == order_id)
        return await database.fetch_one(query)
    
    #! Receive records of all orders by status
    async def getOrderStatusMG(self, status):
        """
        Retrieve MG service orders from the database with a specific status.

        :param str status: Status of the orders to retrieve.
        :return: A list of orders with the given status.
        """
        query = select([BaseOrderMG]).where(BaseOrderMG.status == status)
        return await database.fetch_all(query)
    
    #! Updating order data for the MG
    async def updateOrderMG(self, order_id, status=None, new_order_details=None):
        """
        Update an MG service order in the database with new status and/or order details.

        :param str order_id: ID of the order to update.
        :param str status: New status to set for the order. If None, the status is not updated.
        :param str new_order_details: New order details to set for the order. If None, the order details are not updated.
        :return: The updated order object.
        """
        query = (
            update(BaseOrderMG)
            .where(BaseOrderMG.order_id == order_id)
            .values(status=status if status is not None else BaseOrderMG.status, order_details=new_order_details if new_order_details is not None else BaseOrderMG.order_details)
            .returning(BaseOrderMG)
        )
        return await database.execute(query)
    
    #! Delete order data for the MG
    async def deleteOrderMG(self, order_id):
        """
        Delete an MG service order from the database by its order_id.

        :param str order_id: ID of the order to delete.
        :return: The result of the delete operation.
        """
        query = delete(BaseOrderMG).where(BaseOrderMG.order_id == order_id)
        return await database.execute(query)
    
    #! Creating a new order in the database for the JM service
    async def createOrderJM(self, user_id, zone_id, quantity, price, product, api_name, order_id, message_id, email_user, status, order_details):
        """
        Create a new order for the JM service in the database.

        :param int user_id: ID of the user creating the order.
        :param int zone_id: ID of the zone associated with the order.
        :param int quantity: Quantity of items in the order.
        :param float price: Total price of the order.
        :param str product: Name of the product being ordered.
        :param str api_name: Name of the API used for the order.
        :param str order_id: ID of the order.
        :param int message_id: ID of the message associated with the order.
        :param str email_user: Email of the user creating the order.
        :param str status: Status of the order.
        :param str order_details: Additional details about the order.
        """
        query = BaseOrderJM.__table__.insert().values(
            user_id=user_id,
            zone_id=zone_id,
            quantity=quantity,
            price=price,
            product=product,
            api_name=api_name,
            order_id=order_id,
            message_id=message_id,
            email_user=email_user,
            status=status,
            order_details=order_details,
        )
        await database.execute(query)
    
    #! Receive records of all orders
    async def getAllOrdersJM(self):
        """
        Retrieve records of all JM service orders from the database.

        :return: A list of all JM service orders.
        """
        query = select([BaseOrderJM])
        return await database.fetch_all(query)
    
    #! Receive records of all orders by order_id
    async def getOrderIdJM(self, order_id, message_id):
        """
        Retrieve a JM service order from the database by its order_id and message_id.

        :param str order_id: ID of the order to retrieve.
        :param int message_id: ID of the message associated with the order.
        :return: The order matching the given order_id and message_id or None if not found.
        """
        query = select([BaseOrderJM]).where(BaseOrderJM.order_id == order_id, BaseOrderJM.message_id == message_id)
        return await database.fetch_one(query)
    
    #! Receive records of all orders by status
    async def getOrderStatusJM(self, status):
        """
        Retrieve JM service orders from the database with a specific status.

        :param str status: Status of the orders to retrieve.
        :return: A list of orders with the given status.
        """
        query = select([BaseOrderJM]).where(BaseOrderJM.status == status)
        return await database.fetch_all(query)
    
    #! Updating order data for the JM
    async def updateOrderJM(self, order_id, message_id, status=None, new_order_details=None):
        """
        Update a JM service order in the database with new status and/or order details.

        :param str order_id: ID of the order to update.
        :param int message_id: ID of the message associated with the order.
        :param str status: New status to set for the order. If None, the status is not updated.
        :param str new_order_details: New order details to set for the order. If None, the order details are not updated.
        :return: The updated order object.
        """
        query = (
            update(BaseOrderJM)
            .where(BaseOrderJM.order_id == order_id, BaseOrderJM.message_id == message_id)
            .values(status=status if status is not None else BaseOrderJM.status, order_details=new_order_details if new_order_details is not None else BaseOrderJM.order_details)
            .returning(BaseOrderJM)
        )
        return await database.execute(query)
    
    #! Delete order data for the JM
    async def deleteOrderJM(self, order_id, message_id):
        """
        Delete a JM service order from the database by its order_id and message_id.

        :param str order_id: ID of the order to delete.
        :param int message_id: ID of the message associated with the order to delete.
        :return: The result of the delete operation.
        """
        query = delete(BaseOrderJM).where(BaseOrderJM.order_id == order_id, BaseOrderJM.message_id == message_id)
        return await database.execute(query)
    
    #! Get the number of orders
    async def getCountOrders(self, table):
        """
        Get the count of all orders for a given table.

        :param table: Table class for which to count orders.
        :return: The number of orders in the given table.
        """
        query = select([func.count()]).select_from(table)
        return await database.fetch_val(query)
    
    #! Get the count of orders for the VP
    async def getCountOrderVP(self):
        """
        Get the count of all VP service orders.

        :return: The number of VP service orders in the database.
        """
        return await self.getCountOrders(BaseOrderVP)
    
    #! Get the count of orders for the MG
    async def getCountOrderMG(self):
        """
        Get the count of all MG service orders.

        :return: The number of MG service orders in the database.
        """
        return await self.getCountOrders(BaseOrderMG)
    
    #! Get the count of orders for the JM
    async def getCountOrderJM(self):
        """
        Get the count of all JM service orders.

        :return: The number of JM service orders in the database.
        """
        return await self.getCountOrders(BaseOrderJM)
    
    #! Get the count of orders by status for the VP
    async def getOrderByStatusVP(self):
        """
        Get a list of VP service orders grouped by status.

        :return: A list of VP service orders grouped by status.
        """
        query = select([BaseOrderVP.user_id, BaseOrderVP.order_id, BaseOrderVP.status])#.where(BaseOrderVP.status == "pending")
        return await database.fetch_all(query)
    
    #! Get the count of orders by status for the MG
    async def getOrderByStatusMG(self):
        """
        Get a list of MG service orders grouped by status.

        :return: A list of MG service orders grouped by status.
        """
        query = select([BaseOrderMG.user_id, BaseOrderMG.order_id, BaseOrderMG.status])#.where(BaseOrderMG.status == "pending")
        return await database.fetch_all(query)
    
    #! Get the count of orders by status for the JM
    async def getOrderByStatusJM(self):
        """
        Get a list of JM service orders grouped by status.

        :return: A list of JM service orders grouped by status.
        """
        query = select([BaseOrderJM.user_id, BaseOrderJM.order_id, BaseOrderJM.status])#.where(BaseOrderJM.status == "pending")
        return await database.fetch_all(query)
    
# Instantiating the DatabaseManager to be used in other parts of the application.
db_manager = DatabaseManager()