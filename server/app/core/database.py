from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

connect_args = {}
if settings.is_sqlite:
    connect_args["check_same_thread"] = False
else:
    # Add keepalives to prevent half-open connections from hanging
    connect_args["keepalives"] = 1
    connect_args["keepalives_idle"] = 30
    connect_args["keepalives_interval"] = 10
    connect_args["keepalives_count"] = 5

engine_kwargs = {}
if not settings.is_sqlite:
    engine_kwargs["pool_size"] = 2
    engine_kwargs["max_overflow"] = 3
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300  # Recycle connections every 5 mins
    engine_kwargs["pool_timeout"] = 30   # Wait up to 30s for a connection

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
