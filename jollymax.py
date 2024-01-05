# Importing libraries
import json
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
from base64 import b64encode
from pytz import timezone

# Importing modules
from req_methods import request_creating_order_jm, request_checking_order_jm, request_get_balance
from logger import err_log, func_log

# Class for working API service JOLLYMAX
class ServiceJollymax:
    """
    ServiceJollymax provides asynchronous static methods for interacting with the JOLLYMAX API service.
    It contains methods to get the current timezone, generate unique identifiers, generate digital signatures,
    create orders, check orders, and query account balance.
    """
    
    @staticmethod
    async def get_timezone():
        """
        Gets the current time in Europe/Moscow timezone formatted for API requests.

        Returns:
            str: The current time in the specified timezone formatted according to API requirements.
        """
        current_zone = timezone("Europe/Moscow")
        current_time = datetime.now(current_zone)
        request_time = (
            current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            + current_time.strftime("%z")[:3]
            + ":"
            + current_time .strftime("%z")[3:]
        )
        return request_time
    
    @staticmethod
    async def generate_unique_id(prefix=""):
        """
        Generates a unique identifier string with an optional prefix.

        Args:
            prefix (str, optional): A string to prepend to the generated unique ID. Defaults to an empty string.

        Returns:
            str: A unique identifier string with the specified prefix.
        """
        unique_id = str(uuid.uuid4()).replace("-", "")
        unique_time = datetime.now().strftime("%Y%m%d%H%M%S")
        return prefix + unique_time + unique_id
    
    @staticmethod
    async def generate_signature(payload):
        """
        Generates a digital signature for the given payload using a private RSA key.

        Args:
            payload (dict): The payload for which to generate the digital signature.

        Returns:
            tuple: A tuple containing the base64 encoded digital signature and the JSON encoded payload.
        """
        with open("private.key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )
        payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        signature = private_key.sign(payload_json, padding.PKCS1v15(), hashes.SHA256())
        encoded_signature = b64encode(signature).decode("utf-8")
        return encoded_signature, payload_json
    
    @staticmethod
    async def create_order(uri, api_id, api_no, service, user_id, zone_id, email, quantity, price, product):
        """
        Creates an order through the JOLLYMAX API.

        Args:
            uri (str): The base URI for the API.
            api_id (str): The merchant application ID.
            api_no (str): The merchant number.
            service (str): The service code for the order.
            user_id (str): The user ID for whom the order is being created.
            zone_id (str): The zone ID where the order is applicable.
            email (str): The email address associated with the order.
            quantity (int): The quantity of items in the order.
            price (float): The price of the order.
            product (str): The product code for the order.

        Returns:
            dict: The response from the order creation request.
        """
        api_method = "/distribute-order-create"
        request_time = await ServiceJollymax.get_timezone()
        order_id = await ServiceJollymax.generate_unique_id(prefix="TM003400")
        message_id = await ServiceJollymax.generate_unique_id()
        payload = {
            "requestTime": request_time,
            "version": "1.0",
            "keyVersion": "1",
            "merchantAppId": api_id,
            "merchantNo": api_no,
            "data": {
                "outOrderId": order_id,
                "code": service,
                "quantity": 1,
                "tradeInfo": {
                    "userId": user_id,
                    "serverId": zone_id,
                    "role_id": "",
                },
                "messageId": message_id
            }
        }
        signature, payload_json = await ServiceJollymax.generate_signature(payload)
        headers = { "Content-Type": "application/json", "sign": signature }
        try:
            func_log(f"🔷 Jollymax - Received a new request to create an order from a user: {user_id}")
            return await request_creating_order_jm(
                url=uri + api_method,
                data=payload_json,
                headers=headers,
                order_id=order_id,
                message_id=message_id,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product=product
            )
        except Exception as error:
            err_log(f"🔶 Jollymax - Error function create_order: {error}")
            return { "status": "error", "message": "function create_order", "data": str(error) }
    
    @staticmethod
    async def check_order(uri, api_id, api_no, order_id, message_id):
        """
        Checks the status of an order through the JOLLYMAX API.

        Args:
            uri (str): The base URI for the API.
            api_id (str): The merchant application ID.
            api_no (str): The merchant number.
            order_id (str): The unique identifier of the order to check.
            message_id (str): The message identifier for the order check request.

        Returns:
            dict: The response from the order check request.
        """
        api_method = "/distribute-order-query"
        request_time = await ServiceJollymax.get_timezone()
        payload = {
            "requestTime": request_time,
            "version": "1.0",
            "keyVersion": "1",
            "merchantAppId": api_id,
            "merchantNo": api_no,
            "data": {
                "outOrderId": order_id,
                "messageId": message_id
            }
        }
        signature, payload_json = await ServiceJollymax.generate_signature(payload)
        headers = { "Content-Type": "application/json", "sign": signature }
        try:
            func_log(f"🔷 Jollymax - Received a new request to check an order: {order_id}")
            return await request_checking_order_jm(
                url=uri + api_method,
                data=payload_json,
                headers=headers
            )
        except Exception as error:
            err_log(f"🔶 Jollymax - Error function check_order: {error}")
            return { "status": "error", "message": "function check_order", "data": str(error) }
    
    @staticmethod
    async def balance_query(uri, api_id, api_no):
        """
        Queries the account balance through the JOLLYMAX API.

        Args:
            uri (str): The base URI for the API.
            api_id (str): The merchant application ID.
            api_no (str): The merchant number.

        Returns:
            dict: The response from the balance query request.
        """
        api_method = "/distribute-balance-query"
        request_time = await ServiceJollymax.get_timezone()
        payload = {
            "requestTime": request_time,
            "version": "1.0",
            "keyVersion": "1",
            "merchantAppId": api_id,
            "merchantNo": api_no,
            "data": {},
        }
        signature, payload_json = await ServiceJollymax.generate_signature(payload)
        headers = { "Content-Type": "application/json", "sign": signature }
        try:
            func_log(f"🔷 Jollymax - Received a new request to get balance")
            return await request_get_balance(uri + api_method, payload_json, headers)
        except Exception as error:
            err_log(f"🔶 Jollymax - Error function balance_query: {error}")
            return { "status": "error", "message": "function balance_query", "data": str(error) }