import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models.models import SalesData

# Maps CSV/Excel column headers → SQLAlchemy model attribute names
COLUMN_MAP = {
    "Master Distributor": "master_distributor",
    "Distributor": "distributor",
    "Line of Business": "line_of_business",
    "Supplier": "supplier",
    "Agency": "agency",
    "Category": "category",
    "Segment": "segment",
    "Brand": "brand",
    "Sub Brand": "sub_brand",
    "Country": "country",
    "City": "city",
    "Area": "area",
    "Retailer Group": "retailer_group",
    "Retailer Sub Group": "retailer_sub_group",
    "Channel": "channel",
    "Sub Channel": "sub_channel",
    "Salesmen": "salesmen",
    "Order Number": "order_number",
    "Customer": "customer",
    "Customer Account Name": "customer_account_name",
    "Customer Account Number": "customer_account_number",
    "Item": "item",
    "Item Description": "item_description",
    "Promo Item": "promo_item",
    "Foc/NonFOC": "foc_nonfoc",
    "Unit Selling Price": "unit_selling_price",
    "Invoice Number": "invoice_number",
    "invoice Date": "invoice_date",
    "Year": "year",
    "Month": "month",
    "Invoiced Quantity": "invoiced_quantity",
    "Value": "value",
}

BATCH_SIZE = 1000


def process_upload(file_content, filename: str, db: Session):
    try:
        # ── 1. Read file ──
        if filename.endswith(".csv"):
            df = pd.read_csv(file_content)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_content)
        else:
            return {"error": "Unsupported file format. Please upload .csv or .xlsx"}

        # ── 2. Validate required columns ──
        required_cols = list(COLUMN_MAP.keys())
        # Case-insensitive header matching
        header_map = {col.strip().lower(): col.strip() for col in df.columns}
        renamed = {}
        for req in required_cols:
            lower_req = req.lower()
            if lower_req in header_map:
                renamed[header_map[lower_req]] = req
        df.rename(columns=renamed, inplace=True)

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return {"error": f"Missing required columns: {', '.join(missing)}"}

        rows_processed = len(df)

        # ── 3. Data type conversions (vectorized, on entire DataFrame) ──
        # Parse invoice_date
        df["invoice Date"] = pd.to_datetime(df["invoice Date"], dayfirst=True, errors="coerce")

        # Numeric columns
        for col in ["Unit Selling Price", "Invoiced Quantity", "Value"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

        # Fill NaN strings with empty string for text columns
        text_cols = [k for k, v in COLUMN_MAP.items()
                     if v not in ("unit_selling_price", "invoiced_quantity", "value",
                                  "year", "invoice_date")]
        for col in text_cols:
            df[col] = df[col].astype(str).replace("nan", "").str.strip()

        # ── 4. Truncate old data ──
        db.execute(text("DELETE FROM sales_data"))

        # ── 5. Bulk insert in batches ──
        records = []
        for _, row in df.iterrows():
            record = {}
            for csv_col, db_col in COLUMN_MAP.items():
                val = row[csv_col]
                # Handle NaT / NaN
                if pd.isna(val):
                    record[db_col] = None
                elif db_col == "invoice_date":
                    record[db_col] = val.date() if hasattr(val, "date") else None
                elif db_col == "year":
                    record[db_col] = int(val) if val is not None else None
                else:
                    record[db_col] = val
            records.append(record)

            if len(records) >= BATCH_SIZE:
                db.bulk_insert_mappings(SalesData, records)
                records = []

        # Insert remaining
        if records:
            db.bulk_insert_mappings(SalesData, records)

        db.commit()

        # Sync sequence for PostgreSQL
        try:
            db.execute(text(
                "SELECT setval(pg_get_serial_sequence('sales_data', 'id'), "
                "COALESCE((SELECT MAX(id) FROM sales_data), 0) + 1, false)"
            ))
            db.commit()
        except Exception:
            pass  # SQLite doesn't need sequence sync

        return {
            "summary": "Success",
            "rows_processed": rows_processed,
            "rows_inserted": rows_processed,
            "errors": []
        }

    except Exception as e:
        db.rollback()
        return {"error": f"Failed to process file: {str(e)}"}
