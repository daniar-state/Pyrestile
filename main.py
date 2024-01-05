# Importing libraries
import json
from asyncio import Task, CancelledError, sleep, create_task
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

# Importing modules
from bot import dp, send_message_order
from database import db_manager
from vipayment import ServiceVIPayment
from moogold import ServiceMoogold
from jollymax import ServiceJollymax
from logger import run_log, req_log, func_log, check_log, warn_log, err_log
from config import (
    VP_URI, VP_SECRET_KEY, VP_SIGN,
    MG_URI, MG_SECRET_KEY, MG_PARTNER_ID,
    JM_URI, JM_MERCHANT_ID, JM_MERCHANT_APP_ID,
    VP_STATUSES, MG_STATUSES, JM_STATUSES
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

check_order_task: Task = None
bot_polling_task: Task = None

async def start_bot():
    """
    Initiates the bot polling process.
    """
    await dp.start_polling()

@app.on_event("startup")
async def startup_event():
    """
    Performs setup operations when the application starts up.
    - Connects to the database.
    - Creates tasks for checking order statuses and starting bot polling.
    """
    global check_order_task, bot_polling_task
    await db_manager.connect_db()
    run_log("🔷 Connection database successfully")
    
    check_order_task = create_task(check_order_status())
    run_log("🔷 Check order status task created")
    
    bot_polling_task = create_task(start_bot())
    run_log("🔷 Bot polling task created")
    
    run_log("🔷 Startup event finished")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Performs cleanup operations when the application shuts down.
    - Closes the database connection.
    - Cancels running tasks.
    """
    global check_order_task, bot_polling_task
    await db_manager.close_db()
    run_log("🔷 Connection database closed")
    
    if check_order_task:
        check_order_task.cancel()
        run_log("🔷 Check order status task cancelled")
        try:
            await check_order_task
        except CancelledError:
            pass
    
    if bot_polling_task:
        bot_polling_task.cancel()
        run_log("🔷 Bot polling task cancelled")
        try:
            await bot_polling_task
        except CancelledError:
            pass
    
    session = await dp.bot.get_session()
    await session.close()
    run_log("🔷 Shutdown event finished")

@app.middleware("http")
async def middleware(request: Request, call_next):
    """
    Middleware to log requests and handle exceptions.
    
    :param request: The incoming request object.
    :param call_next: A callable that will receive the request and return a response.
    :return: The response object after processing the request.
    """
    try:
        response = await call_next(request)
        req_log(f"🔷 Request: [{request.method}] {request.url} - Status: {response.status_code}")
    except Exception as error:
        err_log(f"🔶 Request: [{request.method}] {request.url} - Middleware - Error: {error}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "middleware", "data": str(error)})
    return response

@app.get("/")
async def root(request: Request):
    """
    Serves the root HTML page.
    
    :param request: The incoming request object.
    :return: The rendered template response for the root HTML page.
    """
    return templates.TemplateResponse("index.html", { "request": request })

@app.get("/v1")
async def root_api():
    """
    Provides basic information about the API at the root API path.
    
    :return: A JSON response with API status and version information.
    """
    return {
        "status": "active",
        "name": "Skyshop Service API",
        "ver": "1.0.0",
        "message": "Main route",
        "docs": "/docs"
    }

@app.post("/v1/skyshop")
async def skyshop_api(request: Request):
    """
    Handles the skyshop API endpoint for creating orders.

    :param request: The incoming request object.
    :return: A JSON response indicating the success or failure of order creation.
    """
    try:
        data = await request.json()
        if "test" in data:
            return JSONResponse(status_code=200, content={ "status": "success", "message": "testing request successfully", "data": { "test": data["test"] }})
        
        user_id = data.get("Input")
        zone_id = data.get("Zone_ID")
        email = data.get("Email")
        if not all([user_id, zone_id, email]):
            return JSONResponse(status_code=400, content={ "status": "error", "message": "missing parameters", "data": data })
        
        products = data["payment"].get("products", [])
        if not products:
            return JSONResponse(status_code=400, content={ "status": "error", "message": "missing products", "data": data })
        
        first_product = products[0]
        product_name_full = first_product.get("name")
        quantity = first_product.get("quantity")
        price = first_product.get("price")
        if not all([product_name_full, quantity, price]):
            return JSONResponse(status_code=400, content={ "status": "error", "message": "missing product parameters", "data": data })
        
        product_info = product_name_full.split("+")
        if len(product_info) < 3:
            return JSONResponse(status_code=400, content={ "status": "error", "message": "missing product info", "data": data })
        
        service_code = product_info[0]
        product_code = product_info[1]
        product_name = product_info[2]
        
        try:
            func_log("🔷 Getting order data")
            response = await service_create_order(
                service_code=service_code,
                product_code=product_code,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product_name=product_name   
            )
            return JSONResponse(status_code=200, content={"status": "success", "message": "order created", "data": response})
        except Exception as error:
            err_log(f"🔶 Error created order data {error}")
            return JSONResponse(status_code=500, content={"status": "error", "message": "create order", "data": str(error)})
    except Exception as error:
        err_log(f"🔶 Error request data")
        return JSONResponse(status_code=500, content={"status": "error", "message": "request data", "data": str(error)})

async def service_create_order(service_code, product_code, user_id, zone_id, email, quantity, price, product_name):
    """
    Creates an order based on the provided service code and product details.

    :param service_code: The service code indicating which service to use for order creation.
    :param product_code: The code of the product being ordered.
    :param user_id: The ID of the user placing the order.
    :param zone_id: The zone ID associated with the order.
    :param email: The email address of the user.
    :param quantity: The quantity of the product being ordered.
    :param price: The price of the order.
    :param product_name: The name of the product.
    :return: A JSON response with order creation result.
    """
    try:
        if service_code == "VP":
            func_log("🔷 Creating order data for VI Payment")
            await send_message_order(f"🪙 Новый заказ\n\n🌐Сервис платежа: VIPayment\n🔵Название: {product_name}\n🪪Пользователь: {user_id}\n💎Количество: {quantity}\n💲Стоимость: {price} руб.")
            return await ServiceVIPayment.create_order(
                uri=VP_URI,
                api_key=VP_SECRET_KEY,
                sign=VP_SIGN,
                service=product_code,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product=product_name
            )
        elif service_code == "MG":
            func_log("🔷 Creating order data for MooGold")
            await send_message_order(f"🪙 Новый заказ\n\n🌐Сервис платежа: Moogold\n🔵Название: {product_name}\n🪪Пользователь: {user_id}\n💎Количество: {quantity}\n💲Стоимость: {price} руб.")
            return await ServiceMoogold.create_order(
                uri=MG_URI,
                api_key=MG_SECRET_KEY,
                api_id=MG_PARTNER_ID,
                service=product_code,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product=product_name
            )
        elif service_code == "JM":
            func_log("🔷 Creating order data for Jollymax")
            await send_message_order(f"🪙 Новый заказ\n\n🌐Сервис платежа: JollyMax\n🔵Название: {product_name}\n🪪Пользователь: {user_id}\n💎Количество: {quantity}\n💲Стоимость: {price} руб.")
            return await ServiceJollymax.create_order(
                uri=JM_URI,
                api_id=JM_MERCHANT_APP_ID,
                api_no=JM_MERCHANT_ID,
                service=product_code,
                user_id=user_id,
                zone_id=zone_id,
                email=email,
                quantity=quantity,
                price=price,
                product=product_name
            )
        else:
            err_log(f"🔶 Service code not found: {service_code}")
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid service code"})
    except Exception as error:
        err_log(f"🔶 Error create order data")
        return JSONResponse(status_code=500, content={"status": "error", "message": "create order", "data": str(error)})

async def check_order_status():
    """
    Periodically checks the status of orders and updates them accordingly.
    """
    while True:
        try:
            vp_orders = await db_manager.getOrderStatusVP("waiting")
            mg_orders = await db_manager.getOrderStatusMG("processing")
            jm_orders = await db_manager.getOrderStatusJM("waiting")
            
            for vp_order in vp_orders:
                try:
                    order_id = vp_order["order_id"]
                    check_log(f"🔷 Checking order status for VIPayment: {order_id}")
                    orderData = await ServiceVIPayment.check_order(VP_URI, VP_SECRET_KEY, VP_SIGN, order_id)
                    if orderData.get("result") and isinstance(orderData.get("data"), list):
                        data_item = orderData["data"][0] if orderData["data"] else {}
                        new_status = data_item["status"]
                        if new_status in VP_STATUSES:
                            await db_manager.updateOrderVP(
                                order_id=order_id,
                                status=new_status,
                                new_order_details=json.dumps(orderData),
                            )
                            check_log(f"🔷 Order status updated for VIPayment: {order_id} - {new_status}")
                        else:
                            warn_log(f"🔶 Invalid order status for VIPayment: {order_id} - {new_status}")
                    else:
                        warn_log(f"🔶 Invalid order data for VIPayment: {order_id}")
                except Exception as error:
                    err_log(f"🔶 Error checking order status for VIPayment: {order_id} - {error}")
                    continue
            
            for mg_order in mg_orders:
                try:
                    order_id = mg_order["order_id"]
                    check_log(f"🔷 Checking order status for MooGold: {order_id}")
                    orderData = await ServiceMoogold.check_order(MG_URI, MG_SECRET_KEY, MG_PARTNER_ID, order_id)
                    new_status = orderData.get("order_status")
                    if new_status in MG_STATUSES:
                        await db_manager.updateOrderMG(
                                order_id=order_id,
                                status=new_status,
                                new_order_details=json.dumps(orderData),
                        )
                        check_log(f"🔷 Order status updated for MooGold: {order_id} - {new_status}")
                    else:
                        warn_log(f"🔶 Invalid order status for MooGold: {order_id} - {new_status}")
                except Exception as error:
                    err_log(f"🔶 Error checking order status for MooGold: {order_id} - {error}")
                    continue
            
            for jm_order in jm_orders:
                try:
                    order_id = jm_order["order_id"]
                    message_id = jm_order["message_id"]
                    check_log(f"🔷 Checking order status for Jollymax: {order_id}")
                    orderData = await ServiceJollymax.check_order(JM_URI, JM_MERCHANT_APP_ID, JM_MERCHANT_ID, order_id, message_id)
                    new_status = orderData["data"].get("status")
                    if new_status in JM_STATUSES:
                        await db_manager.updateOrderJM(
                            order_id=order_id,
                            message_id=message_id,
                            status=new_status,
                            new_order_details=json.dumps(orderData),
                        )
                        check_log(f"🔷 Order status updated for Jollymax: {order_id} - {new_status}")
                    else:
                        warn_log(f"🔶 Invalid order status for Jollymax: {order_id} - {new_status}")
                except Exception as error:
                    err_log(f"🔶 Error checking order status for Jollymax: {order_id} - {error}")
                    continue
        except Exception as error:
            err_log(f"🔶 Error checking order status: {error}")
            
        await sleep(120)