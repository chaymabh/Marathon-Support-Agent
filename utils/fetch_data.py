
from sqlalchemy import create_engine, MetaData, Table, select

# Replace the following with your actual database connection details
DATABASE_URI = "postgresql+asyncpg://postgres:password123123A@localhost:5432/client_db"

# Create an engine that connects to the PostgreSQL database
engine = create_engine(DATABASE_URI)

# Create a MetaData instance
metadata = MetaData()

# Reflect the tables from the database
metadata.reflect(engine)

# Now you can access your tables using metadata.tables
events_table = metadata.tables['events']
tickets_table = metadata.tables['tickets']
customers_table = metadata.tables['customers']
orders_table = metadata.tables['orders']
faq_table = metadata.tables['faq']
def extract_events():
    with engine.connect() as connection:
        select_query = select([events_table])
        result = connection.execute(select_query)
        for row in result:
            print(row)

def extract_tickets():
    with engine.connect() as connection:
        select_query = select([tickets_table])
        result = connection.execute(select_query)
        for row in result:
            print(row)

def extract_customers():
    with engine.connect() as connection:
        select_query = select([customers_table])
        result = connection.execute(select_query)
        for row in result:
            print(row)

def extract_orders():
    with engine.connect() as connection:
        select_query = select([orders_table])
        result = connection.execute(select_query)
        for row in result:
            print(row)

def extract_faq():
    with engine.connect() as connection:
        select_query = select([faq_table])
        result = connection.execute(select_query)
        for row in result:
            print(row)