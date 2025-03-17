from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import pandas as pd
import datetime

DB_NAME = ".db"
DATABASE_URL = f"sqlite:///./{DB_NAME}"
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../../collected-data/n45")
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
    simple_responses_df = pd.read_excel(os.path.join(DATA_PATH, 'survey_responses.xlsx'), sheet_name='simple_responses')
    delayed_responses_df = pd.read_excel(os.path.join(DATA_PATH, 'survey_responses.xlsx'), sheet_name='delayed_responses')
    
    db = SessionLocal()
    try:
        simple_responses_df.to_sql('responses_simple', con=engine, if_exists='replace', index=False)
        delayed_responses_df.to_sql('responses_multi', con=engine, if_exists='replace', index=False)
    finally:
        db.close()
