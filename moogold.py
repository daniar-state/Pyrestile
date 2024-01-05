# Importing libraries
import json
import hashlib
import base64
import time
import hmac

# Importing modules
from req_methods import request_creating_order_mg, request_checking_order_mg, request_get_products, request_get_find_product
from logger import err_log, func_log

# Class for working API service MOOGOLD
class ServiceMoogold:
    """
    ServiceMoogold provides static methods for interacting with the MOOGOLD API service.
    It includes methods to create authentication tokens and signatures, and to make API requests
    for creating orders, checking orders, and retrieving product information.
    """
    
    @staticmethod
    async def create_auth_token(secret_key, partner_id):
        """
        Creates an authentication token for API requests.

        :param secret_key: The secret key provided by MOOGOLD for API authentication.
        :param partner_id: The partner ID provided by MOOGOLD for API authentication.
        :return: A base64 encoded authentication token.
        """
        auth_token = base64.b64encode(f'{partner_id}:{secret_key}'.encode()).decode()
        func_log(f"🔷 Moogold - Authorization token: {auth_token}")
        return auth_token
    
    @staticmethod
    async def create_auth_signature(secret_key, payload, api_method):
        """
        Creates an authentication signature for API requests.

        :param secret_key: The secret key provided by MOOGOLD for API authentication.
        :param payload: The payload of the request to be signed.
        :param api_method: The API method for the request.
        :return: A tuple containing the HMAC-SHA256 signature and the timestamp used.
        """
        auth_timestamp = str(int(time.time()))
        string_to_sign = payload + auth_timestamp + api_method
        auth_signature = hmac.new(
            bytes(secret_key, 'utf-8'), msg=string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return auth_signature, auth_timestamp
    
    @staticmethod
    async def create_order(uri, api_key, api_id, service, user_id, zone_id, email, quantity, price, product):
        """
        Creates an order through the MOOGOLD API service.

        :param uri: The base URI for the MOOGOLD API service.
        :param api_key: The API key provided by MOOGOLD for API authentication.
        :param api_id: The API ID provided by MOOGOLD for API authentication.
        :param service: The service or product ID for ordering.
        :param user_id: The user ID associated with the order.
        :param zone_id: The game zone ID associated with the order.
        :param email: The email address associated with the order.
        :param quantity: The quantity of the product to order.
        :param price: The price of the product.
        :param product: The product details.
        :return: The response from the create order API request.
        """
        api_method = 'order/create_order'
        payload = {
            "path": "order/create_order",
            "data": {
                "category": "1",
                "product-id": service,
                "quantity": "1",
                "User ID": user_id,
                "Server": zone_id
            }
        }
        data = json.dumps(payload)
        auth_basic_token = await ServiceMoogold.create_auth_token(api_key, api_id)
        auth, time_stamp = await ServiceMoogold.create_auth_signature(api_key, data, api_method)
        headers = {
            "timestamp": time_stamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic_token,
            "Content-Type": "application/json"
        }
        try:
            func_log(f"🔷 Moogold - Received a new request to create an order from a user: {user_id}")
            return await request_creating_order_mg(
                url=uri + api_method,
                data=data,
                headers=headers,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product=product
            )
        except Exception as error:
            err_log(f"🔶 Moogold - Error function create_order: {error}")
            return {
                "status": "error",
                "message": "function create_order",
                "data": str(error)
            }
    
    @staticmethod
    async def check_order(uri, api_key, api_id, order_id):
        """
        Checks the status of an order through the MOOGOLD API service.

        :param uri: The base URI for the MOOGOLD API service.
        :param api_key: The API key provided by MOOGOLD for API authentication.
        :param api_id: The API ID provided by MOOGOLD for API authentication.
        :param order_id: The ID of the order to check.
        :return: The response from the check order API request.
        """
        api_method = 'order/order_detail'
        payload = {
            "path": api_method,
            "order_id": order_id
        }
        data = json.dumps(payload)
        auth_basic_token = await ServiceMoogold.create_auth_token(api_key, api_id)
        auth, time_stamp = await ServiceMoogold.create_auth_signature(api_key, data, api_method)
        headers = {
            "timestamp": time_stamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic_token,
            "Content-Type": "application/json"
        }
        try:
            func_log(f"🔷 Moogold - Received a new request to check an order: {order_id}")
            return await request_checking_order_mg(
                url=uri + api_method,
                data=data,
                headers=headers
            )
        except Exception as error:
            err_log(f"🔶 Moogold - Error function check_order: {error}")
            return {
                "status": "error",
                "message": "function check_order",
                "data": str(error)
            }
    
    @staticmethod
    async def get_products(uri, api_key, api_id, category_id):
        """
        Retrieves a list of products from the MOOGOLD API service based on category ID.

        :param uri: The base URI for the MOOGOLD API service.
        :param api_key: The API key provided by MOOGOLD for API authentication.
        :param api_id: The API ID provided by MOOGOLD for API authentication.
        :param category_id: The category ID to filter products.
        :return: The response from the get products API request.
        """
        api_method = 'product/list_product'
        payload = {
            "path": api_method,
            "category_id": category_id
        }
        data = json.dumps(payload)
        auth_basic_token = await ServiceMoogold.create_auth_token(api_key, api_id)
        auth, time_stamp = await ServiceMoogold.create_auth_signature(api_key, data, api_method)
        headers = {
            "timestamp": time_stamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic_token,
            "Content-Type": "application/json"
        }
        try:
            func_log(f"🔷 Moogold - Received a new request to get products")
            return await request_get_products(uri + api_method, data, headers)
        except Exception as error:
            err_log(f"🔶 Moogold - Error function get_products: {error}")
            return { "status": "error", "message": "function get_products", "data": str(error) }
    
    @staticmethod
    async def get_find_product(uri, api_key, api_id, product_id):
        """
        Retrieves details of a specific product from the MOOGOLD API service.

        :param uri: The base URI for the MOOGOLD API service.
        :param api_key: The API key provided by MOOGOLD for API authentication.
        :param api_id: The API ID provided by MOOGOLD for API authentication.
        :param product_id: The ID of the product to retrieve details for.
        :return: The response from the find product API request.
        """
        api_method = 'product/product_detail'
        payload = {
            "path": api_method,
            "product_id": product_id
        }
        data = json.dumps(payload)
        auth_basic_token = await ServiceMoogold.create_auth_token(api_key, api_id)
        auth, time_stamp = await ServiceMoogold.create_auth_signature(api_key, data, api_method)
        headers = {
            "timestamp": time_stamp,
            "auth": auth,
            "Authorization": "Basic " + auth_basic_token,
            "Content-Type": "application/json"
        }
        try:
            func_log(f"🔷 Moogold - Received a new request to find product")
            return await request_get_find_product(
                uri + api_method,
                data,
                headers
            )
        except Exception as error:
            err_log(f"🔶 Moogold - Error function get_find_product: {error}")
            return {
                "status": "error",
                "message": "function get_find_product",
                "data": str(error)
            }