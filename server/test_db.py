import os
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres.bntgeyuwkxpdohnkztnw:r6pw1bGq7CcIUziT@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"
engine = create_engine(DATABASE_URL, connect_args={'connect_timeout': 5})

try:
    print("Testing connection...", flush=True)
    conn = engine.connect()
    print("Connection successful!", flush=True)
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}", flush=True)
