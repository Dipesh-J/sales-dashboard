from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from ..models.models import SalesData


def _parse_date_range(date_range: str, db: Session = None):
    """Convert frontend dateRange param ('month','quarter','year') to start/end dates.
    Picks the most recent year that has meaningful data (>10 rows)."""
    ref = date.today()
    if db:
        total = db.query(func.count(SalesData.id)).scalar() or 0
        threshold = max(10, int(total * 0.05))

        year_counts = db.query(
            SalesData.year.label("yr"),
            func.count().label("cnt"),
        ).group_by(SalesData.year).order_by(desc(SalesData.year)).all()

        for yr_row in year_counts:
            if yr_row.cnt >= threshold:
                yr = int(yr_row.yr)
                max_in_year = db.query(func.max(SalesData.invoice_date)).filter(
                    SalesData.year == yr
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


def _apply_filters(query, brand=None, category=None, country=None, city=None,
                   channel=None, start_date=None, end_date=None):
    """Apply optional filters to a SalesData query."""
    if brand and brand != "All":
        query = query.filter(SalesData.brand == brand)
    if category and category != "All":
        query = query.filter(SalesData.category == category)
    if country and country != "All":
        query = query.filter(SalesData.country == country)
    if city and city != "All":
        query = query.filter(SalesData.city == city)
    if channel and channel != "All":
        query = query.filter(SalesData.channel == channel)
    if start_date:
        query = query.filter(SalesData.invoice_date >= start_date)
    if end_date:
        query = query.filter(SalesData.invoice_date <= end_date)
    return query


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
    results = db.query(SalesData.brand).distinct().order_by(SalesData.brand).all()
    return [r[0] for r in results if r[0]]


def get_categories(db: Session):
    results = db.query(SalesData.category).distinct().order_by(SalesData.category).all()
    return [r[0] for r in results if r[0]]


def get_regions(db: Session):
    """Returns distinct countries (replaces old 'regions')."""
    results = db.query(SalesData.country).distinct().order_by(SalesData.country).all()
    return [r[0] for r in results if r[0]]


def get_channels(db: Session):
    results = db.query(SalesData.channel).distinct().order_by(SalesData.channel).all()
    return [r[0] for r in results if r[0]]


def get_cities(db: Session):
    results = db.query(SalesData.city).distinct().order_by(SalesData.city).all()
    return [r[0] for r in results if r[0]]


def get_date_range(db: Session):
    result = db.query(func.min(SalesData.invoice_date), func.max(SalesData.invoice_date)).first()
    if result and result[0]:
        return {"min_date": result[0].isoformat(), "max_date": result[1].isoformat()}
    return {"min_date": None, "max_date": None}


# ── Sales services ──

def get_total_sales(db: Session, brand=None, category=None, country=None, city=None,
                    channel=None, date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(func.coalesce(func.sum(SalesData.value), 0))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    total = q.scalar()
    return {"value": round(float(total), 2)}


def get_yoy_sales(db: Session, brand=None, category=None, country=None, city=None,
                  channel=None, date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)

    if not sd or not ed:
        today = date.today()
        ed = today
        sd = today.replace(month=1, day=1)

    q = db.query(func.coalesce(func.sum(SalesData.value), 0))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    current = float(q.scalar())

    prev_sd = sd - relativedelta(years=1)
    prev_ed = ed - relativedelta(years=1)
    q2 = db.query(func.coalesce(func.sum(SalesData.value), 0))
    q2 = _apply_filters(q2, brand, category, country, city, channel, prev_sd, prev_ed)
    previous = float(q2.scalar())

    percent = round(((current - previous) / previous) * 100, 1) if previous else 0
    return {"value": round(current, 2), "percent": percent}


def get_sales_by_brand(db: Session, brand=None, category=None, country=None, city=None,
                       channel=None, date_range=None, start_date=None, end_date=None,
                       page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(SalesData.brand, func.sum(SalesData.value).label("value"))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    q = q.group_by(SalesData.brand).order_by(func.sum(SalesData.value).desc())
    items = [{"brand": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_sales_by_region(db: Session, brand=None, category=None, country=None, city=None,
                        channel=None, date_range=None, start_date=None, end_date=None,
                        page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(SalesData.country, func.sum(SalesData.value).label("value"))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    q = q.group_by(SalesData.country).order_by(func.sum(SalesData.value).desc())
    items = [{"region": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_sales_by_category(db: Session, brand=None, category=None, country=None, city=None,
                          channel=None, date_range=None, start_date=None, end_date=None,
                          page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(SalesData.category, func.sum(SalesData.value).label("value"))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    q = q.group_by(SalesData.category).order_by(func.sum(SalesData.value).desc())
    items = [{"name": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_top_products(db: Session, n=10, brand=None, category=None, country=None, city=None,
                     channel=None, date_range=None, start_date=None, end_date=None,
                     page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(SalesData.item_description, func.sum(SalesData.value).label("value"))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    q = q.group_by(SalesData.item_description).order_by(func.sum(SalesData.value).desc()).limit(n)
    items = [{"name": r[0], "value": round(float(r[1]), 2)} for r in q.all()]
    return _paginate(items, page, page_size)


def get_sales_trend(db: Session, brand=None, category=None, country=None, city=None,
                    channel=None, date_range=None, start_date=None, end_date=None,
                    granularity="month"):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)

    if granularity == "year":
        q = db.query(
            SalesData.year.label("yr"),
            func.sum(SalesData.value).label("value"),
        )
        q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
        q = q.group_by(SalesData.year).order_by(SalesData.year)
        return [{"date": str(int(r[0])), "value": round(float(r[1]), 2)} for r in q.all()]

    elif granularity == "quarter":
        yr_col = extract("year", SalesData.invoice_date).label("yr")
        q_col = ((extract("month", SalesData.invoice_date) - 1) / 3 + 1).label("qtr")
        q = db.query(yr_col, q_col, func.sum(SalesData.value).label("value"))
        q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
        q = q.group_by("yr", "qtr").order_by("yr", "qtr")
        return [{"date": f"{int(r[0])}-Q{int(r[1])}", "value": round(float(r[2]), 2)} for r in q.all()]

    else:  # month (default)
        q = db.query(
            extract("year", SalesData.invoice_date).label("yr"),
            extract("month", SalesData.invoice_date).label("mn"),
            func.sum(SalesData.value).label("value"),
        )
        q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
        q = q.group_by("yr", "mn").order_by("yr", "mn")
        return [{"date": f"{int(r[0])}-{int(r[1]):02d}", "value": round(float(r[2]), 2)} for r in q.all()]


# ── Store / Customer services (adapted from old "active stores") ──

def get_active_stores(db: Session, brand=None, category=None, country=None, city=None,
                      channel=None, date_range=None, start_date=None, end_date=None):
    """Count distinct customers (replaces old active stores)."""
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(func.count(func.distinct(SalesData.customer_account_number)))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    return {"value": q.scalar() or 0}


def get_yoy_active_stores(db: Session, brand=None, category=None, country=None, city=None,
                          channel=None, date_range=None, start_date=None, end_date=None):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    if not sd or not ed:
        today = date.today()
        ed = today
        sd = today.replace(month=1, day=1)

    q = db.query(func.count(func.distinct(SalesData.customer_account_number)))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    current = q.scalar() or 0

    prev_sd = sd - relativedelta(years=1)
    prev_ed = ed - relativedelta(years=1)
    q2 = db.query(func.count(func.distinct(SalesData.customer_account_number)))
    q2 = _apply_filters(q2, brand, category, country, city, channel, prev_sd, prev_ed)
    previous = q2.scalar() or 0

    change = current - previous
    percent = round((change / previous) * 100, 1) if previous else 0
    return {"value": change, "percent": percent}


def get_active_stores_by_region(db: Session, brand=None, category=None, country=None, city=None,
                                channel=None, date_range=None, start_date=None, end_date=None,
                                page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(SalesData.country, func.count(func.distinct(SalesData.customer_account_number)).label("value"))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    q = q.group_by(SalesData.country).order_by(SalesData.country)
    items = [{"region": r[0], "value": r[1]} for r in q.all()]
    return _paginate(items, page, page_size)


def get_active_stores_by_brand(db: Session, brand=None, category=None, country=None, city=None,
                               channel=None, date_range=None, start_date=None, end_date=None,
                               page=1, page_size=20):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)
    q = db.query(SalesData.brand, func.count(func.distinct(SalesData.customer_account_number)).label("value"))
    q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
    q = q.group_by(SalesData.brand).order_by(func.count(func.distinct(SalesData.customer_account_number)).desc())
    items = [{"brand": r[0], "value": r[1]} for r in q.all()]
    return _paginate(items, page, page_size)


def get_active_stores_trend(db: Session, brand=None, category=None, country=None, city=None,
                            channel=None, date_range=None, start_date=None, end_date=None,
                            granularity="month"):
    sd, ed = _resolve_dates(date_range, start_date, end_date, db)

    if granularity == "year":
        q = db.query(
            SalesData.year.label("yr"),
            func.count(func.distinct(SalesData.customer_account_number)).label("value"),
        )
        q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
        q = q.group_by(SalesData.year).order_by(SalesData.year)
        return [{"date": str(int(r[0])), "value": r[1]} for r in q.all()]

    elif granularity == "quarter":
        yr_col = extract("year", SalesData.invoice_date).label("yr")
        q_col = ((extract("month", SalesData.invoice_date) - 1) / 3 + 1).label("qtr")
        q = db.query(
            yr_col, q_col,
            func.count(func.distinct(SalesData.customer_account_number)).label("value"),
        )
        q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
        q = q.group_by("yr", "qtr").order_by("yr", "qtr")
        return [{"date": f"{int(r[0])}-Q{int(r[1])}", "value": r[2]} for r in q.all()]

    else:  # month
        q = db.query(
            extract("year", SalesData.invoice_date).label("yr"),
            extract("month", SalesData.invoice_date).label("mn"),
            func.count(func.distinct(SalesData.customer_account_number)).label("value"),
        )
        q = _apply_filters(q, brand, category, country, city, channel, sd, ed)
        q = q.group_by("yr", "mn").order_by("yr", "mn")
        return [{"date": f"{int(r[0])}-{int(r[1]):02d}", "value": r[2]} for r in q.all()]


def generate_sample_data(db: Session, rows: int = 10):
    import random

    brands = db.query(SalesData.brand).distinct().limit(20).all()
    brands = [r[0] for r in brands if r[0]] or ["Delmond", "Delphy", "Solerone", "Neo"]

    categories = db.query(SalesData.category).distinct().limit(20).all()
    categories = [r[0] for r in categories if r[0]] or ["Biscuits", "Cheese", "Chocolate"]

    countries = db.query(SalesData.country).distinct().limit(10).all()
    countries = [r[0] for r in countries if r[0]] or ["Qatar"]

    cities = db.query(SalesData.city).distinct().limit(10).all()
    cities = [r[0] for r in cities if r[0]] or ["DOHA"]

    channels = db.query(SalesData.channel).distinct().limit(10).all()
    channels = [r[0] for r in channels if r[0]] or ["Minimart"]

    max_date = db.query(func.max(SalesData.invoice_date)).scalar()
    ref_date = max_date if max_date else date.today()

    sample_data = []
    for _ in range(rows):
        brand = random.choice(brands)
        category = random.choice(categories)
        country = random.choice(countries)
        city = random.choice(cities)
        channel = random.choice(channels)
        sale_date = ref_date - timedelta(days=random.randint(0, 365))
        quantity = round(random.uniform(0.5, 100), 2)
        unit_price = round(random.uniform(10.0, 500.0), 2)
        value = round(quantity * unit_price, 2)

        sample_data.append({
            "Master Distributor": "Sample Distributor",
            "Distributor": "Sample Products",
            "Line of Business": "Sample LOB",
            "Supplier": "SAMPLE SUPPLIER",
            "Agency": category,
            "Category": category,
            "Segment": f"{brand} {category}",
            "Brand": brand,
            "Sub Brand": brand,
            "Country": country,
            "City": city,
            "Area": city,
            "Retailer Group": "Sample Retailers",
            "Retailer Sub Group": "Sample Sub Group",
            "Channel": channel,
            "Sub Channel": f"{channel} A",
            "Salesmen": "Sample Salesman",
            "Order Number": str(random.randint(200000, 300000)),
            "Customer": "SAMPLE CUSTOMER",
            "Customer Account Name": "SAMPLE ACCOUNT",
            "Customer Account Number": str(random.randint(10000, 20000)),
            "Item": str(random.randint(1000000000, 9999999999)),
            "Item Description": f"{brand} {category} Sample",
            "Promo Item": "No",
            "Foc/NonFOC": "NONFOC",
            "Unit Selling Price": unit_price,
            "Invoice Number": str(random.randint(300000, 400000)),
            "invoice Date": sale_date.strftime("%-d-%b-%y"),
            "Year": sale_date.year,
            "Month": sale_date.strftime("%b").upper(),
            "Invoiced Quantity": quantity,
            "Value": value,
        })

    return sample_data
