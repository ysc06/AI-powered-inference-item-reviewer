from sqlalchemy.orm import declarative_base 
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
## This script defines a SQLAlchemy ORM model using the declarative style
## The ORM provides an auto-generated __init__ that accepts mapped attributes (so usually don’t write it).
## A model class maps to a database table; each Column(...) defines a table column. An instance of the class represents a row.
## After the module is imported, SQLAlchemy registers the mapping in Base.metadata
## Base.metadata.create_all(bind = engine) -> create table 
## Column() defines a column’s type and constraints

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(32), default="ai")   
    prompt = Column(Text, nullable=True)
    stimulus = Column(Text, nullable=True)     
    stem = Column(Text, nullable=True)
    choices = Column(Text, nullable=False)      
    answer = Column(String(8), nullable=False)  
    meta_json = Column("metadata", Text, nullable=True)    # variable changed to meta to avoid but keep 'metadata' in database
    status = Column(Text, nullable = False)
    committed = Column(Text, nullable = True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
