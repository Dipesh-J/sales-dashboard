import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models import models

def _sync_sequence(db: Session, table_name: str, id_column: str = "id"):
    """Sync PostgreSQL auto-increment sequence with existing data."""
    try:
        db.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', '{id_column}'), "
            f"COALESCE((SELECT MAX({id_column}) FROM {table_name}), 0) + 1, false)"
        ))
    except Exception:
        pass  # SQLite doesn't need sequence sync

def process_upload(file_content, filename: str, db: Session):
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file_content)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_content)
        else:
            return {"error": "Unsupported file format. Please upload .csv or .xlsx"}

        required_cols = ['Product Name', 'Brand', 'Category', 'Region', 'Store ID', 'Date', 'Quantity', 'Value']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return {"error": f"Missing required columns: {', '.join(missing)}"}

        rows_processed = len(df)
        rows_inserted = 0
        errors = []

        # Sync sequences to avoid primary key conflicts on re-upload
        _sync_sequence(db, "regions")
        _sync_sequence(db, "products")
        _sync_sequence(db, "sales")

        for index, row in df.iterrows():
            try:
                # 1. UPSERT Region
                region_name = str(row['Region']).strip()
                region = db.query(models.Region).filter_by(name=region_name).first()
                if not region:
                    region = models.Region(name=region_name)
                    db.add(region)
                    db.flush()

                # 2. UPSERT Store
                store_id = int(row['Store ID'])
                store = db.query(models.Store).filter_by(id=store_id).first()
                if not store:
                    store = models.Store(id=store_id, region_id=region.id)
                    db.add(store)
                    db.flush()

                # 3. UPSERT Product
                product_name = str(row['Product Name']).strip()
                brand = str(row['Brand']).strip()
                category = str(row['Category']).strip()
                product = db.query(models.Product).filter_by(name=product_name, brand=brand, category=category).first()
                if not product:
                    product = models.Product(name=product_name, brand=brand, category=category)
                    db.add(product)
                    db.flush()

                # 4. INSERT Sale
                sale_date = pd.to_datetime(row['Date']).date()
                quantity = int(row['Quantity'])
                value = float(row['Value'])

                existing_sale = db.query(models.Sale).filter_by(
                    product_id=product.id,
                    store_id=store.id,
                    date=sale_date,
                    quantity=quantity,
                    value=value
                ).first()

                if not existing_sale:
                    sale = models.Sale(
                        product_id=product.id,
                        store_id=store.id,
                        date=sale_date,
                        quantity=quantity,
                        value=value
                    )
                    db.add(sale)

                db.commit()
                rows_inserted += 1

            except Exception as e:
                db.rollback()
                errors.append(f"Row {index + 1}: {str(e)}")

        return {
            "summary": "Success",
            "rows_processed": rows_processed,
            "rows_inserted": rows_inserted,
            "errors": errors[:10]
        }

    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}
