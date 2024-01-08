from sqlalchemy import Column, Integer, String
from database import Base

class InviteORM(Base):
    __tablename__ = 'alice'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer)