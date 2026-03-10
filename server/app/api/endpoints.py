from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal

from ..core.database import get_db
from ..core.cache import cached, invalidate_all, TTL_FILTERS, TTL_DASHBOARD
from ..services.upload import process_upload
from ..services import services

router = APIRouter()

# Data Upload Endpoint
@router.post("/data/upload", summary="Upload sales data", description="Accepts .xlsx or .csv file. Parses, validates columns, truncates old data, and bulk-inserts all rows. Invalidates all cached dashboard data.", tags=["Upload"])
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    import io
    file_stream = io.BytesIO(content) if file.filename.endswith((".xlsx", ".xls")) else io.StringIO(content.decode('utf-8'))

    result = process_upload(file_stream, file.filename, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    invalidate_all()
    return result

@router.get("/data/sample", summary="Generate sample sales data", description="Generates random sample rows based on existing db categories.", tags=["Upload"])
def get_sample_data(rows: int = 10, db: Session = Depends(get_db)):
    return services.generate_sample_data(db, rows)

# Sales Metrics
@router.get("/sales/total", summary="Get total sales value", tags=["Sales"])
@cached("sales_total")
def get_total_sales(dateRange: Optional[str] = None, brand: Optional[str] = None,
                    category: Optional[str] = None, region: Optional[str] = None,
                    city: Optional[str] = None, channel: Optional[str] = None,
                    start_date: Optional[str] = None, end_date: Optional[str] = None,
                    db: Session = Depends(get_db)):
    return services.get_total_sales(db, brand=brand, category=category, country=region,
                                    city=city, channel=channel,
                                    date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/yoy", summary="Get year-over-year sales growth", tags=["Sales"])
@cached("sales_yoy")
def get_yoy_sales(dateRange: Optional[str] = None, brand: Optional[str] = None,
                  category: Optional[str] = None, region: Optional[str] = None,
                  city: Optional[str] = None, channel: Optional[str] = None,
                  start_date: Optional[str] = None, end_date: Optional[str] = None,
                  db: Session = Depends(get_db)):
    return services.get_yoy_sales(db, brand=brand, category=category, country=region,
                                  city=city, channel=channel,
                                  date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/sales/by-brand", summary="Get sales grouped by brand", tags=["Sales"])
@cached("sales_by_brand")
def get_sales_by_brand(dateRange: Optional[str] = None, brand: Optional[str] = None,
                       category: Optional[str] = None, region: Optional[str] = None,
                       city: Optional[str] = None, channel: Optional[str] = None,
                       start_date: Optional[str] = None, end_date: Optional[str] = None,
                       page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                       db: Session = Depends(get_db)):
    return services.get_sales_by_brand(db, brand=brand, category=category, country=region,
                                       city=city, channel=channel,
                                       date_range=dateRange, start_date=start_date, end_date=end_date,
                                       page=page, page_size=page_size)

@router.get("/sales/by-region", summary="Get sales grouped by country", tags=["Sales"])
@cached("sales_by_region")
def get_sales_by_region(dateRange: Optional[str] = None, brand: Optional[str] = None,
                        category: Optional[str] = None, region: Optional[str] = None,
                        city: Optional[str] = None, channel: Optional[str] = None,
                        start_date: Optional[str] = None, end_date: Optional[str] = None,
                        page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        db: Session = Depends(get_db)):
    return services.get_sales_by_region(db, brand=brand, category=category, country=region,
                                        city=city, channel=channel,
                                        date_range=dateRange, start_date=start_date, end_date=end_date,
                                        page=page, page_size=page_size)

@router.get("/sales/by-category", summary="Get sales grouped by category", tags=["Sales"])
@cached("sales_by_category")
def get_sales_by_category(dateRange: Optional[str] = None, brand: Optional[str] = None,
                          category: Optional[str] = None, region: Optional[str] = None,
                          city: Optional[str] = None, channel: Optional[str] = None,
                          start_date: Optional[str] = None, end_date: Optional[str] = None,
                          page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                          db: Session = Depends(get_db)):
    return services.get_sales_by_category(db, brand=brand, category=category, country=region,
                                          city=city, channel=channel,
                                          date_range=dateRange, start_date=start_date, end_date=end_date,
                                          page=page, page_size=page_size)

@router.get("/sales/top-products", summary="Get top N products by sales", tags=["Sales"])
@cached("sales_top_products")
def get_top_products(n: int = 10, dateRange: Optional[str] = None, brand: Optional[str] = None,
                     category: Optional[str] = None, region: Optional[str] = None,
                     city: Optional[str] = None, channel: Optional[str] = None,
                     start_date: Optional[str] = None, end_date: Optional[str] = None,
                     page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                     db: Session = Depends(get_db)):
    return services.get_top_products(db, n=n, brand=brand, category=category, country=region,
                                     city=city, channel=channel,
                                     date_range=dateRange, start_date=start_date, end_date=end_date,
                                     page=page, page_size=page_size)

@router.get("/sales/trend", summary="Get sales trend over time", tags=["Sales"])
@cached("sales_trend")
def get_sales_trend(dateRange: Optional[str] = None, brand: Optional[str] = None,
                    category: Optional[str] = None, region: Optional[str] = None,
                    city: Optional[str] = None, channel: Optional[str] = None,
                    start_date: Optional[str] = None, end_date: Optional[str] = None,
                    granularity: Literal["month", "quarter", "year"] = "month",
                    db: Session = Depends(get_db)):
    return services.get_sales_trend(db, brand=brand, category=category, country=region,
                                    city=city, channel=channel,
                                    date_range=dateRange, start_date=start_date, end_date=end_date,
                                    granularity=granularity)

# Active Customers Metrics (backward-compatible with /stores/* paths)
@router.get("/stores/active", summary="Get total active customers count", tags=["Stores"])
@cached("stores_active")
def get_active_stores(dateRange: Optional[str] = None, brand: Optional[str] = None,
                      category: Optional[str] = None, region: Optional[str] = None,
                      city: Optional[str] = None, channel: Optional[str] = None,
                      start_date: Optional[str] = None, end_date: Optional[str] = None,
                      db: Session = Depends(get_db)):
    return services.get_active_stores(db, brand=brand, category=category, country=region,
                                      city=city, channel=channel,
                                      date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/stores/active/yoy", summary="Get YoY active customers change", tags=["Stores"])
@cached("stores_active_yoy")
def get_yoy_active_stores(dateRange: Optional[str] = None, brand: Optional[str] = None,
                          category: Optional[str] = None, region: Optional[str] = None,
                          city: Optional[str] = None, channel: Optional[str] = None,
                          start_date: Optional[str] = None, end_date: Optional[str] = None,
                          db: Session = Depends(get_db)):
    return services.get_yoy_active_stores(db, brand=brand, category=category, country=region,
                                          city=city, channel=channel,
                                          date_range=dateRange, start_date=start_date, end_date=end_date)

@router.get("/stores/active/by-region", summary="Get active customers by country", tags=["Stores"])
@cached("stores_by_region")
def get_active_stores_by_region(dateRange: Optional[str] = None, brand: Optional[str] = None,
                                category: Optional[str] = None, region: Optional[str] = None,
                                city: Optional[str] = None, channel: Optional[str] = None,
                                start_date: Optional[str] = None, end_date: Optional[str] = None,
                                page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                                db: Session = Depends(get_db)):
    return services.get_active_stores_by_region(db, brand=brand, category=category, country=region,
                                                city=city, channel=channel,
                                                date_range=dateRange, start_date=start_date, end_date=end_date,
                                                page=page, page_size=page_size)

@router.get("/stores/active/by-brand", summary="Get active customers by brand", tags=["Stores"])
@cached("stores_by_brand")
def get_active_stores_by_brand(dateRange: Optional[str] = None, brand: Optional[str] = None,
                               category: Optional[str] = None, region: Optional[str] = None,
                               city: Optional[str] = None, channel: Optional[str] = None,
                               start_date: Optional[str] = None, end_date: Optional[str] = None,
                               page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                               db: Session = Depends(get_db)):
    return services.get_active_stores_by_brand(db, brand=brand, category=category, country=region,
                                               city=city, channel=channel,
                                               date_range=dateRange, start_date=start_date, end_date=end_date,
                                               page=page, page_size=page_size)

@router.get("/stores/active/trend", summary="Get active customers trend over time", tags=["Stores"])
@cached("stores_trend")
def get_active_stores_trend(dateRange: Optional[str] = None, brand: Optional[str] = None,
                            category: Optional[str] = None, region: Optional[str] = None,
                            city: Optional[str] = None, channel: Optional[str] = None,
                            start_date: Optional[str] = None, end_date: Optional[str] = None,
                            granularity: Literal["month", "quarter", "year"] = "month",
                            db: Session = Depends(get_db)):
    return services.get_active_stores_trend(db, brand=brand, category=category, country=region,
                                            city=city, channel=channel,
                                            date_range=dateRange, start_date=start_date, end_date=end_date,
                                            granularity=granularity)

# Filters
@router.get("/filters/brands", summary="Get available brands", tags=["Filters"])
@cached("filter_brands", ttl=TTL_FILTERS)
def get_brands(db: Session = Depends(get_db)):
    return services.get_brands(db)

@router.get("/filters/categories", summary="Get available categories", tags=["Filters"])
@cached("filter_categories", ttl=TTL_FILTERS)
def get_categories(db: Session = Depends(get_db)):
    return services.get_categories(db)

@router.get("/filters/regions", summary="Get available countries/regions", tags=["Filters"])
@cached("filter_regions", ttl=TTL_FILTERS)
def get_regions(db: Session = Depends(get_db)):
    return services.get_regions(db)

@router.get("/filters/channels", summary="Get available channels", tags=["Filters"])
@cached("filter_channels", ttl=TTL_FILTERS)
def get_channels(db: Session = Depends(get_db)):
    return services.get_channels(db)

@router.get("/filters/cities", summary="Get available cities", tags=["Filters"])
@cached("filter_cities", ttl=TTL_FILTERS)
def get_cities(db: Session = Depends(get_db)):
    return services.get_cities(db)

@router.get("/filters/date-range", summary="Get date range bounds", tags=["Filters"])
@cached("filter_date_range", ttl=TTL_FILTERS)
def get_date_range(db: Session = Depends(get_db)):
    return services.get_date_range(db)
