from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..services.upload import process_upload
from ..services import services

router = APIRouter()

# Data Upload Endpoint
@router.post("/data/upload")
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Accepts .xlsx or .csv. Parses, validates, and upserts."""
    content = await file.read()
    import io
    file_stream = io.BytesIO(content) if file.filename.endswith((".xlsx", ".xls")) else io.StringIO(content.decode('utf-8'))

    result = process_upload(file_stream, file.filename, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

# Sales Metrics
@router.get("/sales/total")
def get_total_sales(dateRange: Optional[str] = None, brand: Optional[str] = None,
                    category: Optional[str] = None, region: Optional[str] = None,
                    start_date: Optional[str] = None, end_date: Optional[str] = None,
                    db: Session = Depends(get_db)):
    return services.get_total_sales(db, brand=brand, category=category, region=region,
                                    date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/yoy")
def get_yoy_sales(dateRange: Optional[str] = None, brand: Optional[str] = None,
                  category: Optional[str] = None, region: Optional[str] = None,
                  start_date: Optional[str] = None, end_date: Optional[str] = None,
                  db: Session = Depends(get_db)):
    return services.get_yoy_sales(db, brand=brand, category=category, region=region,
                                  date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/by-brand")
def get_sales_by_brand(dateRange: Optional[str] = None, brand: Optional[str] = None,
                       category: Optional[str] = None, region: Optional[str] = None,
                       start_date: Optional[str] = None, end_date: Optional[str] = None,
                       db: Session = Depends(get_db)):
    return services.get_sales_by_brand(db, brand=brand, category=category, region=region,
                                       date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/by-region")
def get_sales_by_region(dateRange: Optional[str] = None, brand: Optional[str] = None,
                        category: Optional[str] = None, region: Optional[str] = None,
                        start_date: Optional[str] = None, end_date: Optional[str] = None,
                        db: Session = Depends(get_db)):
    return services.get_sales_by_region(db, brand=brand, category=category, region=region,
                                        date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/by-category")
def get_sales_by_category(dateRange: Optional[str] = None, brand: Optional[str] = None,
                          category: Optional[str] = None, region: Optional[str] = None,
                          start_date: Optional[str] = None, end_date: Optional[str] = None,
                          db: Session = Depends(get_db)):
    return services.get_sales_by_category(db, brand=brand, category=category, region=region,
                                          date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/top-products")
def get_top_products(n: int = 10, dateRange: Optional[str] = None, brand: Optional[str] = None,
                     category: Optional[str] = None, region: Optional[str] = None,
                     start_date: Optional[str] = None, end_date: Optional[str] = None,
                     db: Session = Depends(get_db)):
    return services.get_top_products(db, n=n, brand=brand, category=category, region=region,
                                     date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/trend")
def get_sales_trend(dateRange: Optional[str] = None, brand: Optional[str] = None,
                    category: Optional[str] = None, region: Optional[str] = None,
                    start_date: Optional[str] = None, end_date: Optional[str] = None,
                    db: Session = Depends(get_db)):
    return services.get_sales_trend(db, brand=brand, category=category, region=region,
                                    date_range=dateRange, start_date=start_date, end_date=end_date)

# Active Stores Metrics
@router.get("/stores/active")
def get_active_stores(dateRange: Optional[str] = None, brand: Optional[str] = None,
                      category: Optional[str] = None, region: Optional[str] = None,
                      start_date: Optional[str] = None, end_date: Optional[str] = None,
                      db: Session = Depends(get_db)):
    return services.get_active_stores(db, brand=brand, category=category, region=region,
                                      date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/stores/active/yoy")
def get_yoy_active_stores(dateRange: Optional[str] = None, brand: Optional[str] = None,
                          category: Optional[str] = None, region: Optional[str] = None,
                          start_date: Optional[str] = None, end_date: Optional[str] = None,
                          db: Session = Depends(get_db)):
    return services.get_yoy_active_stores(db, brand=brand, category=category, region=region,
                                          date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/stores/active/by-region")
def get_active_stores_by_region(dateRange: Optional[str] = None, brand: Optional[str] = None,
                                category: Optional[str] = None, region: Optional[str] = None,
                                start_date: Optional[str] = None, end_date: Optional[str] = None,
                                db: Session = Depends(get_db)):
    return services.get_active_stores_by_region(db, brand=brand, category=category, region=region,
                                                date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/stores/active/by-brand")
def get_active_stores_by_brand(dateRange: Optional[str] = None, brand: Optional[str] = None,
                                category: Optional[str] = None, region: Optional[str] = None,
                                start_date: Optional[str] = None, end_date: Optional[str] = None,
                                db: Session = Depends(get_db)):
    return services.get_active_stores_by_brand(db, brand=brand, category=category, region=region,
                                                date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/stores/active/trend")
def get_active_stores_trend(dateRange: Optional[str] = None, brand: Optional[str] = None,
                            category: Optional[str] = None, region: Optional[str] = None,
                            start_date: Optional[str] = None, end_date: Optional[str] = None,
                            db: Session = Depends(get_db)):
    return services.get_active_stores_trend(db, brand=brand, category=category, region=region,
                                            date_range=dateRange, start_date=start_date, end_date=end_date)

# Utilities
@router.get("/filters/brands")
def get_brands(db: Session = Depends(get_db)):
    return services.get_brands(db)

@router.get("/filters/categories")
def get_categories(db: Session = Depends(get_db)):
    return services.get_categories(db)

@router.get("/filters/regions")
def get_regions(db: Session = Depends(get_db)):
    return services.get_regions(db)

@router.get("/filters/date-range")
def get_date_range(db: Session = Depends(get_db)):
    return services.get_date_range(db)
