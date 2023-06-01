from sqlalchemy import Column, Integer, DateTime, CheckConstraint
from datetime import datetime


class BaseModel:
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
