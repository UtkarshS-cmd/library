
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

BASE_URL = os.getenv(
 'BASE_URL',
 'postgresql://postgres:141205@localhost:5432/social-media')
engine = create_engine(
 BASE_URL,
 echo=True, # prints every SQL statement — very useful for learning
 pool_size=5, # keep 5 connections open in pool
 max_overflow=10, # allow up to 10 extra connections if needed
 )
# Test the connection
with engine.connect() as conn:
    print("Connected successfully!")
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())
