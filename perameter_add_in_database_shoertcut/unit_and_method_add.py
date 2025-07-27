import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def insert_unit_and_protocol():
    # Step 1: Load Excel
    excel_file = "perameter_add_in_database_shoertcut/processed_parameters.xlsx"
    df = pd.read_excel(excel_file)

    # Clean param names for comparison
    df["param_name_clean"] = df["Processed_Name"].astype(str).str.strip().str.lower()

    # Step 2: Connect to DB
    engine = create_engine(DB_URL)

    with engine.begin() as connection:
        # Get all existing DB parameter names
        result = connection.execute(text("SELECT name FROM parameters"))
        db_names = [name.strip().lower() for name in result.scalars().all() if name]

        updated = 0
        inserted = 0

        for _, row in df.iterrows():
            name_clean = row["param_name_clean"]
            unit = row.get("Unit")
            is_3025_method = row.get("IS 3025 Method")
            apha_method = row.get("APHA 24th Edition Method")
            original_name = row.get("Processed_Name")

            # Clean and validate
            unit = None if pd.isna(unit) else unit
            is_3025_method = None if pd.isna(is_3025_method) else is_3025_method
            apha_method = None if pd.isna(apha_method) else apha_method
            original_name_cleaned = str(original_name).strip() if pd.notna(original_name) else None

            # Find matches in DB where name contains Excel name
            matched_names = [
                db_name for db_name in db_names
                if name_clean in db_name
            ]

            if matched_names:
                # ✅ Update all DB rows where name LIKE %excel_name%
                connection.execute(text(f"""
                    UPDATE parameters
                    SET unit = :unit,
                        is_3025_method = :is_method,
                        apha_24th_edition_method = :apha_method
                    WHERE LOWER(name) LIKE :like_pattern
                """), {
                    "unit": unit,
                    "is_method": is_3025_method,
                    "apha_method": apha_method,
                    "like_pattern": f"%{name_clean}%"
                })
                updated += len(matched_names)
            elif original_name_cleaned:
                # ➕ Insert if no match found
                connection.execute(text("""
                    INSERT INTO parameters (name, unit, is_3025_method, apha_24th_edition_method)
                    VALUES (:name, :unit, :is_method, :apha_method)
                """), {
                    "name": original_name_cleaned,
                    "unit": unit,
                    "is_method": is_3025_method,
                    "apha_method": apha_method
                })
                inserted += 1

    # Step 3: Summary
    print("\n✅ Update Summary")
    print(f"✔️  Updated rows: {updated}")
    print(f"➕  Inserted new rows: {inserted}")

# Run the function
# insert_unit_and_protocol()
