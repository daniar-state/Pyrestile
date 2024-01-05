# Importing libraries
from sqlalchemy import Column, MetaData, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from databases import Database

# Importing modules
from config import DB_URI

# Creating a database engine
engine = create_engine(DB_URI)
metadata = MetaData()
Base = declarative_base()

#* Creating a basic database model for the VP service
class BaseOrderVP(Base):
    """
    Represents a basic database model for the VP service.
    
    Attributes:
        id (Column): The primary key, an autoincrementing integer.
        user_id (Column): A string representing the user identifier.
        zone_id (Column): A string representing the zone identifier.
        quantity (Column): An integer representing the quantity of an order.
        price (Column): A string representing the price of the order.
        product (Column): A string representing the product name.
        api_name (Column): A string representing the API name associated with the order.
        order_id (Column): A string representing the unique order identifier.
        email_user (Column): A string representing the email of the user.
        status (Column): A string representing the status of the order.
        order_details (Column): A text column for any additional details about the order.
    """
    __tablename__ = "vp_orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    zone_id = Column(String)
    quantity = Column(Integer)
    price = Column(String)
    product = Column(String)
    api_name = Column(String)
    order_id = Column(String)
    email_user = Column(String)
    status = Column(String)
    order_details = Column(Text)

#* Creating a basic database model for the MG service
class BaseOrderMG(Base):
    """
    Represents a basic database model for the MG service.
    
    Attributes are similar to BaseOrderVP with the same data types and purposes.
    """
    __tablename__ = "mg_orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    zone_id = Column(String)
    quantity = Column(Integer)
    price = Column(String)
    product = Column(String)
    api_name = Column(String)
    order_id = Column(String)
    email_user = Column(String)
    status = Column(String)
    order_details = Column(Text)

#* Creating a basic database model for the JM service
class BaseOrderJM(Base):
    """
    Represents a basic database model for the JM service.
    
    Attributes are similar to BaseOrderVP with the addition of a message_id attribute.
    
    Attributes:
        message_id (Column): A string representing the message identifier, specific to JM service.
    """
    __tablename__ = "jm_orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    zone_id = Column(String)
    quantity = Column(Integer)
    price = Column(String)
    product = Column(String)
    api_name = Column(String)
    order_id = Column(String)
    message_id = Column(String)
    email_user = Column(String)
    status = Column(String)
    order_details = Column(Text)

#* Creating tables by models
def create_base_tables():
    """
    Creates all the tables in the database based on the defined models.
    
    It connects to the database using the Database URI from the config module and initializes the tables.
    """
    Base.metadata.create_all(engine)

database = Database(DB_URI)
