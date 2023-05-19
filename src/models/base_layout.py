from sqlalchemy import Column, Integer, DateTime
from datetime import datetime


class BaseModel:
    id = Column(Integer(), primary_key=True, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
