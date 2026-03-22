from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile = Column(String(15), unique=True, index=True)
    hashed_password = Column(String)
    is_registered = Column(Boolean, default=False)
    is_logged_in = Column(Boolean, default=False)
