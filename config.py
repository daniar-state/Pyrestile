# * Server configurations
ENV_MODE = "development"  # development or production
LOCAL_HOST = "localhost"
LOCAL_PORT = 3000
SERVER_HOST = "91.227.18.168"
SERVER_PORT = 20000

#! Don't change this
# * Database configurations (PostgreSQL)
DB_URI = "postgresql://developer_base:Qwerty%23123@91.227.18.168:5432/skyshop_database"
# * Telegram configurations (Aiogram)
TG_TOKEN_TEST = "6701016616:AAHHN8uRsxQWB8EdopSa7BtEA9D47KXdOtI"
TG_TOKEN = "6932044010:AAF66X9p-mdqO9LB10OhB_ZlLomKfC3ntFQ"
TG_ADMINS = ["6668365200", "295785929"]
# * VIPAYMENT configurations
VP_URI = "https://vip-reseller.co.id/api"
VP_APP_ID = "tUVjjJoh"
VP_SECRET_KEY = "6g2qBEbxK0YvIQ9ojgwoTms2ErytYUOt8KRcEEhLerdW0HvOBE0rHjOpHePU1YcL"
VP_SIGN = "046dc0200622a8e84d6e97d0c7f92481"
# * MOOGOLD configurations
MG_URI = "https://moogold.com/wp-json/v1/api/"
MG_SECRET_KEY = "PxHxb4fEFN"
MG_PARTNER_ID = "4669dd809f4159177329f958904c2c47"
# * JOLLYMAX configurations
JM_URI = "https://api.jollymax.com/aggregate-pay/api/gateway"
JM_MERCHANT_ID = "P01010115486674"
JM_MERCHANT_APP_ID = "88617ddabe384692af21c1fa81a8b177"
# * PAYMENT'S statuses
VP_STATUSES = ["success", "error"]
MG_STATUSES = ["completed", "failed"]
JM_STATUSES = ["SUCC", "FAIL"]