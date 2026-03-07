"""
Generate comprehensive seed data CSV for the Sales Dashboard.
Run: python seed_data.py
Output: seed_data.csv (in current directory)
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

BRANDS = ["Nike", "Adidas", "Puma", "Reebok", "Under Armour"]
CATEGORIES = ["Footwear", "Apparel", "Accessories", "Equipment"]
REGIONS = ["North", "South", "East", "West", "Central"]

PRODUCTS = {
    "Nike": {
        "Footwear": ["Nike Air Max", "Nike Pegasus", "Nike Dunk"],
        "Apparel": ["Nike Dri-FIT Tee", "Nike Pro Shorts"],
        "Accessories": ["Nike Cap", "Nike Socks Pack"],
        "Equipment": ["Nike Training Bag"],
    },
    "Adidas": {
        "Footwear": ["Adidas Ultraboost", "Adidas Superstar"],
        "Apparel": ["Adidas Tiro Pants", "Adidas Essentials Tee"],
        "Accessories": ["Adidas Headband", "Adidas Water Bottle"],
        "Equipment": ["Adidas Gym Ball"],
    },
    "Puma": {
        "Footwear": ["Puma RS-X", "Puma Suede Classic"],
        "Apparel": ["Puma Track Jacket", "Puma Logo Tee"],
        "Accessories": ["Puma Beanie"],
        "Equipment": ["Puma Resistance Band Set"],
    },
    "Reebok": {
        "Footwear": ["Reebok Classic Leather", "Reebok Nano X"],
        "Apparel": ["Reebok CrossFit Tee", "Reebok Joggers"],
        "Accessories": ["Reebok Wristband"],
        "Equipment": ["Reebok Yoga Mat"],
    },
    "Under Armour": {
        "Footwear": ["UA HOVR Phantom", "UA Charged Assert"],
        "Apparel": ["UA HeatGear Tee", "UA Rival Fleece Hoodie"],
        "Accessories": ["UA Sport Mask"],
        "Equipment": ["UA Duffel Bag"],
    },
}

# Assign store IDs to regions (20 stores per region = 100 total)
STORES_PER_REGION = 20
stores_by_region = {}
store_id = 1
for region in REGIONS:
    stores_by_region[region] = list(range(store_id, store_id + STORES_PER_REGION))
    store_id += STORES_PER_REGION

# Date range: 2023-01-01 to 2025-12-31
start = date(2023, 1, 1)
end = date(2025, 12, 31)
all_dates = []
d = start
while d <= end:
    all_dates.append(d)
    d += timedelta(days=1)

# Build flat product list
product_list = []
for brand, cats in PRODUCTS.items():
    for category, names in cats.items():
        for name in names:
            product_list.append((name, brand, category))

rows = []
# Generate ~2500 sale records spread across time
for _ in range(2500):
    sale_date = random.choice(all_dates)
    region = random.choice(REGIONS)
    store_id_val = random.choice(stores_by_region[region])
    product_name, brand, category = random.choice(product_list)

    # Value scales by year to create YoY growth pattern
    year_multiplier = 1.0 + (sale_date.year - 2023) * 0.15
    base_value = random.uniform(20, 500)
    quantity = random.randint(1, 20)
    value = round(base_value * quantity * year_multiplier, 2)

    rows.append({
        "Product Name": product_name,
        "Brand": brand,
        "Category": category,
        "Region": region,
        "Store ID": store_id_val,
        "Date": sale_date.isoformat(),
        "Quantity": quantity,
        "Value": value,
    })

output_file = "seed_data.csv"
with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Product Name", "Brand", "Category", "Region", "Store ID", "Date", "Quantity", "Value"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} rows → {output_file}")
