from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from ..models.models import Sale, Product, Store, Region


def _parse_date_range(date_range: str, db: Session = None):
    """Convert frontend dateRange param ('month','quarter','year') to start/end dates.
    Uses the latest date in the database as the reference point so dashboards
    always show the most recent data available."""
    ref = date.today()
    if db:
        max_date = db.query(func.max(Sale.date)).scalar()
        if max_date:
            ref = max_date

    if date_range == "month":
        start = ref.replace(day=1)
    elif date_range == "quarter":
        q_month = ((ref.month - 1) // 3) * 3 + 1
        start = ref.replace(month=q_month, day=1)
    elif date_range == "year":
        start = ref.replace(month=1, day=1)
    else:
        return None, None
    return start, ref


def _apply_filters(query, brand=None, category=None, region=None, start_date=None, end_date=None):
    """Apply optional filters to a query that already joins Product/Store/Region as needed."""
    if brand and brand != "All":
        query = query.filter(Product.brand == brand)
    if category and category != "All":
        query = query.filter(Product.category == category)
    if region and region != "All":
        query = query.filter(Region.name == region)
    if start_date:
        query = query.filter(Sale.date >= start_date)
    if end_date:
        query = query.filter(Sale.date <= end_date)
    return query


def _base_sale_query(db: Session):
    """Base query joining Sale→Product, Sale→Store→Region."""
    return db.query(Sale).join(Product, Sale.product_id == Product.id).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)


def _resolve_dates(date_range, start_date, end_date, db: Session = None):
    """Resolve dates from either explicit params or dateRange shortcut."""
    if start_date and end_date:
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        return start_date, end_date
    if date_range:
        return _parse_date_range(date_range, db)
    return None, None


# ── Filter endpoints ──

def get_brands(db: Session):
    results = db.query(Product.brand).distinct().order_by(Product.brand).all()
    return [r[0] for r in results]


def get_categories(db: Session):
    results = db.query(Product.category).distinct().order_by(Product.category).all()
    return [r[0] for r in results]


def get_regions(db: Session):
    results = db.query(Region.name).distinct().order_by(Region.name).all()
    return [r[0] for r in results]


def get_date_range(db: Session):
    result = db.query(func.min(Sale.date), func.max(Sale.date)).first()
    if result and result[0]:
        return {"min_date": result[0].isoformat(), "max_date": result[1].isoformat()}
    return {"min_date": None, "max_date": None}


# ── Sales services ──

def get_total_sales(db: Session, brand=None, category=None, region=None,
                    date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(func.coalesce(func.sum(Sale.value), 0)).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    total = q.scalar()
    return {"value": round(float(total), 2)}


def get_yoy_sales(db: Session, brand=None, category=None, region=None,
                  date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)

    # If no dates resolved, use current year vs previous year
    if not sd or not ed:
        today = date.today()
        ed = today
        sd = today.replace(month=1, day=1)

    # Current period
    q = db.query(func.coalesce(func.sum(Sale.value), 0)).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    current = float(q.scalar())

    # Previous period (same range shifted back 1 year)
    prev_sd = sd - relativedelta(years=1)
    prev_ed = ed - relativedelta(years=1)
    q2 = db.query(func.coalesce(func.sum(Sale.value), 0)).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q2 = _apply_filters(q2, brand, category, region, prev_sd, prev_ed)
    previous = float(q2.scalar())

    percent = round(((current - previous) / previous) * 100, 1) if previous else 0
    return {"value": round(current, 2), "percent": percent}


def get_sales_by_brand(db: Session, brand=None, category=None, region=None,
                       date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.brand, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.brand).order_by(func.sum(Sale.value).desc())
    return [{"brand": r[0], "value": round(float(r[1]), 2)} for r in q.all()]


def get_sales_by_region(db: Session, brand=None, category=None, region=None,
                        date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Region.name, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Region.name).order_by(func.sum(Sale.value).desc())
    return [{"region": r[0], "value": round(float(r[1]), 2)} for r in q.all()]


def get_sales_by_category(db: Session, brand=None, category=None, region=None,
                          date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.category, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.category).order_by(func.sum(Sale.value).desc())
    return [{"name": r[0], "value": round(float(r[1]), 2)} for r in q.all()]


def get_top_products(db: Session, n=10, brand=None, category=None, region=None,
                     date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.name, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.name).order_by(func.sum(Sale.value).desc()).limit(n)
    return [{"name": r[0], "value": round(float(r[1]), 2)} for r in q.all()]


def get_sales_trend(db: Session, brand=None, category=None, region=None,
                    date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    # Group by year-month
    q = db.query(
        extract("year", Sale.date).label("yr"),
        extract("month", Sale.date).label("mn"),
        func.sum(Sale.value).label("value"),
    ).join(Product, Sale.product_id == Product.id).join(
        Store, Sale.store_id == Store.id
    ).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by("yr", "mn").order_by("yr", "mn")
    results = []
    for r in q.all():
        yr, mn = int(r[0]), int(r[1])
        label = f"{yr}-{mn:02d}"
        results.append({"date": label, "value": round(float(r[2]), 2)})
    return results


# ── Store services ──

def get_active_stores(db: Session, brand=None, category=None, region=None,
                      date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(func.count(func.distinct(Sale.store_id))).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    return {"value": q.scalar() or 0}


def get_yoy_active_stores(db: Session, brand=None, category=None, region=None,
                          date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    if not sd or not ed:
        today = date.today()
        ed = today
        sd = today.replace(month=1, day=1)

    q = db.query(func.count(func.distinct(Sale.store_id))).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    current = q.scalar() or 0

    prev_sd = sd - relativedelta(years=1)
    prev_ed = ed - relativedelta(years=1)
    q2 = db.query(func.count(func.distinct(Sale.store_id))).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q2 = _apply_filters(q2, brand, category, region, prev_sd, prev_ed)
    previous = q2.scalar() or 0

    change = current - previous
    percent = round((change / previous) * 100, 1) if previous else 0
    return {"value": change, "percent": percent}


def get_active_stores_by_region(db: Session, brand=None, category=None, region=None,
                                date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Region.name, func.count(func.distinct(Sale.store_id)).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Region.name).order_by(Region.name)
    return [{"region": r[0], "value": r[1]} for r in q.all()]


def get_active_stores_by_brand(db: Session, brand=None, category=None, region=None,
                                date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.brand, func.count(func.distinct(Sale.store_id)).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.brand).order_by(func.count(func.distinct(Sale.store_id)).desc())
    return [{"brand": r[0], "value": r[1]} for r in q.all()]


def get_active_stores_trend(db: Session, brand=None, category=None, region=None,
                            date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(
        extract("year", Sale.date).label("yr"),
        extract("month", Sale.date).label("mn"),
        func.count(func.distinct(Sale.store_id)).label("value"),
    ).join(Product, Sale.product_id == Product.id).join(
        Store, Sale.store_id == Store.id
    ).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by("yr", "mn").order_by("yr", "mn")
    results = []
    for r in q.all():
        yr, mn = int(r[0]), int(r[1])
        label = f"{yr}-{mn:02d}"
        results.append({"date": label, "value": r[2]})
    return results
