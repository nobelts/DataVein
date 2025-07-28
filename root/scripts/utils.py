def load_env_variables():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    return {
        "S3": os.getenv("S3"),
        "DB_URL": os.getenv("DB_URL"),
        "JWT_SECRET": os.getenv("JWT_SECRET"),
    }

def connect_to_db(db_url):
    import sqlalchemy

    engine = sqlalchemy.create_engine(db_url)
    return engine.connect()

def health_check():
    return {"status": "healthy"}