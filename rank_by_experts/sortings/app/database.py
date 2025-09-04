from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import pandas as pd
import datetime


DB_NAME = ".db"
DATABASE_URL = f"sqlite:///./{DB_NAME}"
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../../../collected-data/toa")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db():
    # save a copy of the database
    if os.path.exists(DB_NAME):
        os.rename(DB_NAME, f'{DB_NAME}.{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.bak')
    
    # create a new database and save the schema
    Base.metadata.create_all(bind=engine)


def init_db():
    create_db()
    
    orders_df = pd.read_excel(os.path.join(DATA_PATH, 'orders.xlsx'))
    # pick 5 from each qid
    orders_df = orders_df.groupby('qid').head(7)
    orders_df['qid'] = orders_df['qid'].astype(int)
    orders_df['orders_id'] = orders_df['orders_id'].astype(int)
    orders_df.to_sql('orders', con=engine, if_exists='append', index=False)
