from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from models import Base

class Database:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """Initialize database and create tables"""
        Base.metadata.create_all(bind=self.engine)
        print("Database initialized successfully!")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close database session"""
        session.close()

# Singleton database instance
db = Database()