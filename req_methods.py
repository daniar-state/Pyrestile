# Importing libraries
import json
import httpx

# Importing modules
from database import db_manager
from logger import db_log, warn_log, err_log, func_log, check_log

async def request_creating_order_vp(url: str, data: dict, headers: dict, user_id, zone_id, email, quantity, price, product):
    """
    Asynchronously sends a request to create a VIPAYMENT order and logs the process.
    
    :param url: API endpoint to create the order.
    :param data: Data payload for the POST request.
    :param headers: Headers for the POST request.
    :param user_id: The ID of the user making the order.
    :param zone_id: The ID of the zone where the user is located.
    :param email: The email address of the user.
    :param quantity: The quantity of the product ordered.
    :param price: The price of the product ordered.
    :param product: The product that is being ordered.
    :return: A transaction ID if successful, or a status dictionary indicating failure.
    """
    try:
        func_log(f"🔷 Vipayment - Sending a request to create an order from user: {user_id}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            func_log(f"🔷 Vipayment - A request to create an order from user: {user_id} was successfully processed with status: {response.status_code}")
            if data["result"] == True:
                vp_trxid = data["data"]["trxid"]
                func_log(f"🔷 Vipayment - Order from user: {user_id} was successfully created...")
                await db_manager.createOrderVP(
                    user_id=user_id,
                    zone_id=zone_id,
                    quantity=quantity,
                    price=price,
                    product=product,
                    api_name="VIPAYMENT",
                    order_id=vp_trxid,
                    email_user=email,
                    status="waiting",
                    order_details=json.dumps(data)
                )
                db_log(f"🔷 Vipayment - An order from user: {user_id} was successfully added to the database")
                return vp_trxid
            else:
                warn_log(f"🔶 Vipayment - An order from user: {user_id} was not created. Status: {data['result']}. Reason: {data}")
                return { "status": "warning", "message": "order creation failed", "data": data }
        else:
            err_log(f"🔶 Vipayment - A request to create an order from user: {user_id} was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "user_id": user_id, "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 Vipayment - An error occurred inside a function (creating order). Error: {error}")
        return { "status": "exception", "user_id": user_id, "message": "function error: (creating order)", "data": str(error)}

async def request_creating_order_mg(url: str, data: dict, headers: dict, user_id, zone_id, email, quantity, price, product):
    """
    Asynchronously sends a request to create a MOOGOLD order and logs the process.

    Similar parameters and return type as request_creating_order_vp.
    """
    func_log(f"🔷 Moogold - Sending a request to create an order from user: {user_id}")
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, data=data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        func_log(f"🔷 Moogold - A request to create an order from user: {user_id} was successfully processed with status: {response.status_code}")
        func_log(f"Moogold response: {data}")
        if data["status"] == True:
            # if "status" in data and data["status"] == True:
            func_log(f"🔷 Moogold - Order from user: {user_id} was successfully created...")
            mg_trxid = data["account_details"]["order_id"]
            await db_manager.createOrderMG(
                user_id=user_id,
                zone_id=zone_id,
                quantity=quantity,
                price=price,
                product=product,
                api_name="MOOGOLD",
                order_id=mg_trxid,
                email_user=email,
                status="processing",
                order_details=json.dumps(data),
            )
            db_log(f"🔷 Moogold - An order from user: {user_id} was successfully added to the database")
            return mg_trxid
        else:
            warn_log(f"🔶 Moogold - An order from user: {user_id} was not created. Status: {data['status']}. Reason: {data}")
            return { "status": "warning", "message": "order creation failed", "data": data }
    else:
        err_log(f"🔶 Moogold - A request to create an order from user: {user_id} was not processed. Status: {response.status_code}. Reason: {response}")
        return { "status": "error", "user_id": user_id, "message": "the request failed", "data": response }

async def request_creating_order_jm(url: str, data: dict, headers: dict, order_id, message_id, user_id, zone_id, email, quantity, price, product):
    """
    Asynchronously sends a request to create a JOLLYMAX order and logs the process.

    Additional parameters:
    :param order_id: The ID of the order.
    :param message_id: The message ID associated with the order.
    """
    try:
        func_log(f"🔷 Jollymax - Sending a request to create an order from user: {user_id}")
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            func_log(f"🔷 Jollymax - A request to create an order from user: {user_id} was successfully processed with status: {response.status_code}")
            if data["code"] == "APPLY_SUCCESS":
                func_log(f"🔷 Jollymax - Order from user: {user_id} was successfully created...")
                await db_manager.createOrderJM(
                    user_id=user_id,
                    zone_id=zone_id,
                    quantity=quantity,
                    price=price,
                    product=product,
                    api_name="JOLLYMAX",
                    order_id=order_id,
                    message_id=message_id,
                    email_user=email,
                    status="waiting",
                    order_details=json.dumps(data),
                )
                db_log(f"🔷 Jollymax - An order from user: {user_id} was successfully added to the database")
                return order_id, message_id
            else:
                warn_log(f"🔶 Jollymax - An order from user: {user_id} was not created. Status: {data['code']}. Reason: {data}")
                return { "status": "warning", "message": "order creation failed", "data": data }
        else:
            err_log(f"🔶 Jollymax - A request to create an order from user: {user_id} was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "user_id": user_id, "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 Jollymax - An error occurred inside a function (creating order). Error: {error}")
        return { "status": "exception", "user_id": user_id, "message": "function error: (creating order)", "data": str(error)}

async def request_checking_order_vp(url: str, data: dict, headers: dict):
    """
    Asynchronously sends a request to check the status of a VIPAYMENT order.
    
    Similar parameters as request_creating_order_vp, but without user details and product info.
    :return: Order data if successful, or a status dictionary indicating failure.
    """
    try:
        check_log(f"🔷 Vipayment - Sending a request to check the order")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            check_log(f"🔷 Vipayment - A request to check the order was successfully processed with status: {response.status_code}")
            if data["result"] == True:
                check_log(f"🔷 Vipayment - Order was successfully checked...")
                return data
            else:
                warn_log(f"🔶 Vipayment - Order was not checked. Status: {data['result']}. Reason: {data}")
                return { "status": "warning", "message": "order check failed", "data": data }
        else:
            err_log(f"🔶 Vipayment - A request to check the order was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 Vipayment - An error occurred inside a function (checking order). Error: {error}")
        return { "status": "exception", "message": "function error: (checking order)", "data": str(error)}

async def request_checking_order_mg(url: str, data: dict, headers: dict):
    """
    Asynchronously sends a request to check the status of a MOOGOLD order.

    Similar parameters and return type as request_checking_order_vp.
    """
    try:
        check_log(f"🔷 Moogold - Sending a request to check the order")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            check_log(f"🔷 Moogold - A request to check the order was successfully processed with status: {response.status_code}")
            if "order_status" in data and data["order_status"] == "completed":
                check_log(f"🔷 Moogold - Order was successfully paid...")
                return data
            else:
                warn_log(f"🔶 Moogold - Order was not paid. Status: {data['order_status']}. Reason: {data}")
                return { "status": "warning", "message": "order not paid", "data": data }
        else:
            err_log(f"🔶 Moogold - A request to check the order was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 Moogold - An error occurred inside a function (checking order). Error: {error}")
        return { "status": "exception", "message": "function error: (checking order)", "data": str(error)}

async def request_checking_order_jm(url: str, data: dict, headers: dict):
    """
    Asynchronously sends a request to check the status of a JOLLYMAX order.

    Similar parameters and return type as request_checking_order_vp.
    """
    try:
        check_log(f"🔷 Jollymax - Sending a request to check the order")
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            check_log(f"🔷 Jollymax - A request to check the order was successfully processed with status: {response.status_code}")
            if data["code"] == "APPLY_SUCCESS":
                check_log(f"🔷 Jollymax - Order was successfully paid...")
                return data
            else:
                warn_log(f"🔶 Jollymax - Order was not paid. Status: {data['code']}. Reason: {data}")
                return { "status": "warning", "message": "order not paid", "data": data }
        else:
            err_log(f"🔶 Jollymax - A request to check the order was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 Jollymax - An error occurred inside a function (checking order). Error: {error}")
        return { "status": "exception", "message": "function error: (checking order)", "data": str(error)}

async def request_get_products(url: str, data: dict, headers: dict):
    """
    Asynchronously sends a request to retrieve the list of products.
    
    :param url: API endpoint to get the products.
    :param data: Data payload for the POST request.
    :param headers: Headers for the POST request.
    :return: List of products if successful, or a status dictionary indicating failure.
    """
    try:
        func_log(f"🔷 Getting a list of products...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            func_log(f"🔷 A request to get a list of products was successfully processed with status: {response.status_code}")
            return { "status": "success", "message": "list of products received successfully", "data": data }
        else:
            err_log(f"🔶 A request to get a list of products was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 An error occurred inside a function (getting a list of products). Error: {error}")
        return { "status": "exception", "message": "function error: (getting a list of products)", "data": str(error)}

async def request_get_find_product(url: str, data: dict, headers: dict):
    """
    Asynchronously sends a request to retrieve details of a single product.

    Similar parameters and return type as request_get_products.
    """
    try:
        func_log(f"🔷 Getting a product...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            func_log(f"🔷 A request to get a product was successfully processed with status: {response.status_code}")
            return { "status": "success", "message": "product received successfully", "data": data }
        else:
            err_log(f"🔶 A request to get a product was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 An error occurred inside a function (getting a product). Error: {error}")
        return { "status": "exception", "message": "function error: (getting a product)", "data": str(error)}  

async def request_get_balance(url: str, data: dict, headers: dict):
    """
    Asynchronously sends a request to retrieve the current balance.
    
    :param url: API endpoint to get the balance.
    :param data: Data payload for the POST request.
    :param headers: Headers for the POST request.
    :return: Balance data if successful, or a status dictionary indicating failure.
    """
    try:
        func_log(f"🔷 Getting a balance...")
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url=url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data["code"] == "APPLY_SUCCESS":
                func_log(f"🔷 A request to get a balance was successfully processed with status: {response.status_code}")
                jm_balance = data["data"].get("balance")
                return { "status": "success", "message": "balance received successfully", "jm_balance": jm_balance }
            else:
                warn_log(f"🔶 A request to get a balance was not processed. Status: {data['code']}. Reason: {data}")
                return { "status": "warning", "message": "balance not received", "data": data }
        else:
            err_log(f"🔶 A request to get a balance was not processed. Status: {response.status_code}. Reason: {response}")
            return { "status": "error", "message": "the request failed", "data": response }
    except Exception as error:
        err_log(f"🔶 An error occurred inside a function (getting a balance). Error: {error}")
        return { "status": "exception", "message": "function error: (getting a balance)", "data": str(error)}