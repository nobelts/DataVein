from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base, YourModel  # Import your models here
import os

DATABASE_URL = os.getenv("DB_URL", "postgresql://user:password@localhost/dbname")

def seed_database():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the database tables
    Base.metadata.create_all(engine)

    # Add initial data
    initial_data = [
        YourModel(field1='value1', field2='value2'),  # Replace with your model fields
        YourModel(field1='value3', field2='value4'),
    ]

    session.add_all(initial_data)
    session.commit()
    session.close()

if __name__ == "__main__":
    seed_database()