from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, literal_column
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from ..models.models import Sale, Product, Store, Region


def _parse_date_range(date_range: str, db: Session = None):
    """Convert frontend dateRange param ('month','quarter','year') to start/end dates.
    Picks the most recent year that has meaningful data (>10 rows), ignoring stray
    future rows that would otherwise shift the dashboard to a near-empty year."""
    ref = date.today()
    if db:
        total = db.query(func.count(Sale.id)).scalar() or 0
        # Threshold: a year needs at least 10 rows or 5% of total data
        threshold = max(10, int(total * 0.05))

        # Get years with their row counts, most recent first
        from sqlalchemy import desc
        year_counts = db.query(
            extract("year", Sale.date).label("yr"),
            func.count().label("cnt"),
        ).group_by("yr").order_by(desc("yr")).all()

        for yr_row in year_counts:
            if yr_row.cnt >= threshold:
                yr = int(yr_row.yr)
                max_in_year = db.query(func.max(Sale.date)).filter(
                    extract("year", Sale.date) == yr
                ).scalar()
                if max_in_year:
                    ref = max_in_year
                break

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


def _paginate(items, page, page_size):
    """Apply pagination to an in-memory list and return wrapped response."""
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {"data": items[start:end], "total": total, "page": page, "page_size": page_size}


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
                       date_range=None, start_date=None, end_date=None,
                       page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.brand, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.brand).order_by(func.sum(Sale.value).desc())
    items = [{"brand": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_sales_by_region(db: Session, brand=None, category=None, region=None,
                        date_range=None, start_date=None, end_date=None,
                        page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Region.name, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Region.name).order_by(func.sum(Sale.value).desc())
    items = [{"region": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_sales_by_category(db: Session, brand=None, category=None, region=None,
                          date_range=None, start_date=None, end_date=None,
                          page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.category, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.category).order_by(func.sum(Sale.value).desc())
    items = [{"name": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_top_products(db: Session, n=10, brand=None, category=None, region=None,
                     date_range=None, start_date=None, end_date=None,
                     page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.name, func.sum(Sale.value).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.name).order_by(func.sum(Sale.value).desc()).limit(n)
    items = [{"name": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_sales_trend(db: Session, brand=None, category=None, region=None,
                    date_range=None, start_date=None, end_date=None,
                    granularity="month"):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)

    if granularity == "year":
        q = db.query(
            extract("year", Sale.date).label("yr"),
            func.sum(Sale.value).label("value"),
        ).join(Product, Sale.product_id == Product.id).join(
            Store, Sale.store_id == Store.id
        ).join(Region, Store.region_id == Region.id)
        q = _apply_filters(q, brand, category, region, sd, ed)
        q = q.group_by("yr").order_by("yr")
        return [{"date": str(int(r[0])), "value": round(float(r[1]), 2)} for r in q.all()]

    elif granularity == "quarter":
        yr_col = extract("year", Sale.date).label("yr")
        q_col = ((extract("month", Sale.date) - 1) / 3 + 1).label("qtr")
        q = db.query(
            yr_col, q_col,
            func.sum(Sale.value).label("value"),
        ).join(Product, Sale.product_id == Product.id).join(
            Store, Sale.store_id == Store.id
        ).join(Region, Store.region_id == Region.id)
        q = _apply_filters(q, brand, category, region, sd, ed)
        q = q.group_by("yr", "qtr").order_by("yr", "qtr")
        return [{"date": f"{int(r[0])}-Q{int(r[1])}", "value": round(float(r[2]), 2)} for r in q.all()]

    else:  # month (default)
        q = db.query(
            extract("year", Sale.date).label("yr"),
            extract("month", Sale.date).label("mn"),
            func.sum(Sale.value).label("value"),
        ).join(Product, Sale.product_id == Product.id).join(
            Store, Sale.store_id == Store.id
        ).join(Region, Store.region_id == Region.id)
        q = _apply_filters(q, brand, category, region, sd, ed)
        q = q.group_by("yr", "mn").order_by("yr", "mn")
        return [{"date": f"{int(r[0])}-{int(r[1]):02d}", "value": round(float(r[2]), 2)} for r in q.all()]


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
                                date_range=None, start_date=None, end_date=None,
                                page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Region.name, func.count(func.distinct(Sale.store_id)).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Region.name).order_by(Region.name)
    items = [{"region": r[0], "value": r[1]} for r in q.all()]
    return _paginate(items, page, page_size)


def get_active_stores_by_brand(db: Session, brand=None, category=None, region=None,
                                date_range=None, start_date=None, end_date=None,
                                page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(Product.brand, func.count(func.distinct(Sale.store_id)).label("value")).join(
        Product, Sale.product_id == Product.id
    ).join(Store, Sale.store_id == Store.id).join(Region, Store.region_id == Region.id)
    q = _apply_filters(q, brand, category, region, sd, ed)
    q = q.group_by(Product.brand).order_by(func.count(func.distinct(Sale.store_id)).desc())
    items = [{"brand": r[0], "value": r[1]} for r in q.all()]
    return _paginate(items, page, page_size)


def get_active_stores_trend(db: Session, brand=None, category=None, region=None,
                            date_range=None, start_date=None, end_date=None,
                            granularity="month"):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)

    if granularity == "year":
        q = db.query(
            extract("year", Sale.date).label("yr"),
            func.count(func.distinct(Sale.store_id)).label("value"),
        ).join(Product, Sale.product_id == Product.id).join(
            Store, Sale.store_id == Store.id
        ).join(Region, Store.region_id == Region.id)
        q = _apply_filters(q, brand, category, region, sd, ed)
        q = q.group_by("yr").order_by("yr")
        return [{"date": str(int(r[0])), "value": r[1]} for r in q.all()]

    elif granularity == "quarter":
        yr_col = extract("year", Sale.date).label("yr")
        q_col = ((extract("month", Sale.date) - 1) / 3 + 1).label("qtr")
        q = db.query(
            yr_col, q_col,
            func.count(func.distinct(Sale.store_id)).label("value"),
        ).join(Product, Sale.product_id == Product.id).join(
            Store, Sale.store_id == Store.id
        ).join(Region, Store.region_id == Region.id)
        q = _apply_filters(q, brand, category, region, sd, ed)
        q = q.group_by("yr", "qtr").order_by("yr", "qtr")
        return [{"date": f"{int(r[0])}-Q{int(r[1])}", "value": r[2]} for r in q.all()]

    else:  # month (default)
        q = db.query(
            extract("year", Sale.date).label("yr"),
            extract("month", Sale.date).label("mn"),
            func.count(func.distinct(Sale.store_id)).label("value"),
        ).join(Product, Sale.product_id == Product.id).join(
            Store, Sale.store_id == Store.id
        ).join(Region, Store.region_id == Region.id)
        q = _apply_filters(q, brand, category, region, sd, ed)
        q = q.group_by("yr", "mn").order_by("yr", "mn")
        return [{"date": f"{int(r[0])}-{int(r[1]):02d}", "value": r[2]} for r in q.all()]


def generate_sample_data(db: Session, rows: int = 10):
    import random

    # Fetch whole product tuples (name, brand, category) to keep them consistent
    product_tuples = db.query(Product.name, Product.brand, Product.category).distinct().limit(50).all()
    if not product_tuples:
        product_tuples = [
            ("Nike Air Max 90", "Nike", "Footwear"),
            ("Adidas Ultraboost 24", "Adidas", "Footwear"),
            ("Puma Logo Tee", "Puma", "Apparel"),
            ("UA Rival Fleece Hoodie", "Under Armour", "Apparel"),
            ("Reebok Nano X4", "Reebok", "Footwear"),
        ]

    # Fetch store-region pairs to keep them consistent
    store_region_pairs = db.query(Store.id, Region.name).join(
        Region, Store.region_id == Region.id
    ).all()
    if not store_region_pairs:
        store_region_pairs = [
            (101, "North"), (102, "North"),
            (201, "South"), (202, "South"),
            (301, "East"), (302, "East"),
            (401, "West"), (402, "West"),
        ]

    # Use max date in DB as upper bound to avoid generating future dates
    max_date = db.query(func.max(Sale.date)).scalar()
    ref_date = max_date if max_date else date.today()

    sample_data = []

    for _ in range(rows):
        name, brand, category = random.choice(product_tuples)
        store_id, region = random.choice(store_region_pairs)
        sale_date = ref_date - timedelta(days=random.randint(0, 365))
        quantity = random.randint(1, 100)
        unit_price = round(random.uniform(10.0, 250.0), 2)
        sample_data.append({
            "Product Name": name,
            "Brand": brand,
            "Category": category,
            "Region": region,
            "Store ID": store_id,
            "Date": sale_date.isoformat(),
            "Quantity": quantity,
            "Value": round(quantity * unit_price, 2)
        })

    return sample_data
