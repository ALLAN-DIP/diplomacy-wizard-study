from app.models import Base
from app.database import engine, get_db, init_db

if __name__ == "__main__":
    init_db()
    print("Database initialized")
