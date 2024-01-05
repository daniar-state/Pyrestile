# Importing modules
from req_methods import request_creating_order_vp, request_checking_order_vp
from logger import err_log, func_log

# * Class for working API service VIPAYMENT
class ServiceVIPayment:
    """
    Class to interact with the VIPAYMENT API service.
    
    Attributes:
        HEADERS (dict): Headers to be used in the API requests.
    """

    HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "curl/7.64.1"
    }

    @staticmethod
    async def create_order(uri, api_key, sign, service, user_id, zone_id, email, quantity, price, product):
        """
        Creates an order with the VIPAYMENT service.
        
        Args:
            uri (str): The base URI of the VIPAYMENT API.
            api_key (str): API key for authentication.
            sign (str): Signature for the request validation.
            service (str): The service identifier.
            user_id (str): The user ID.
            zone_id (str): The zone ID.
            email (str): The user's email address.
            quantity (int): The quantity of the product.
            price (float): The price of the product.
            product (str): The product identifier.
        
        Returns:
            A coroutine that resolves to the response from the VIPAYMENT API service.
        """
        api_method = "/game-feature"
        payload = {
            "key": api_key,
            "sign": sign,
            "type": "order",
            "service": service,
            "data_no": user_id,
            "data_zone": zone_id
        }
        try:
            func_log(f"🔷 Vipayment - Received a new request to create an order from a user: {user_id}")
            return await request_creating_order_vp(
                url=uri + api_method,
                data=payload,
                headers=ServiceVIPayment.HEADERS,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product=product
            )
        except Exception as error:
            err_log(f"🔶 Vipayment - Error function create_order: {error}")
            return {
                "status": "error",
                "message": "function create_order",
                "data": str(error)
            }

    @staticmethod
    async def check_order(uri, api_key, sign, order_id):
        """
        Checks the status of an existing order with the VIPAYMENT service.
        
        Args:
            uri (str): The base URI of the VIPAYMENT API.
            api_key (str): API key for authentication.
            sign (str): Signature for the request validation.
            order_id (str): The order ID to check.
        
        Returns:
            A coroutine that resolves to the response from the VIPAYMENT API service.
        """
        api_method = "/game-feature"
        payload = {
            "key": api_key,
            "sign": sign,
            "type": "status",
            "trxid": order_id
        }
        try:
            func_log(f"🔷 Vipayment - Received a new request to check an order: {order_id}")
            return await request_checking_order_vp(
                url=uri + api_method,
                data=payload,
                headers=ServiceVIPayment.HEADERS
            )
        except Exception as error:
            err_log(f"🔶 Vipayment - Error function check_order: {error}")
            return {
                "status": "error",
                "message": "function check_order",
                "data": str(error)
            }