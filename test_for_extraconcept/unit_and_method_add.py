import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")  # Example: postgresql://user:password@localhost/dbname

# Step 1: Read Excel File
excel_file = "processed_parameters.xlsx"  # Update path if needed
df = pd.read_excel(excel_file)

# Clean parameter names for matching
df["param_name_clean"] = df["Processed_Name"].astype(str).str.strip().str.lower()

# Step 2: Connect to DB with auto-commit enabled
engine = create_engine(DB_URL)

with engine.begin() as connection:  # ✅ BEGIN a transaction (commits automatically)
    # Fetch all existing parameter names from DB
    result = connection.execute(text("SELECT id, name FROM parameters"))
    param_rows = result.mappings().all()

    # Create mapping: cleaned_name -> id
    db_param_map = {row["name"].strip().lower(): row["id"] for row in param_rows}

    updated = 0
    unmatched = []

    for _, row in df.iterrows():
        name_clean = row["param_name_clean"]
        param_id = db_param_map.get(name_clean)

        if param_id:
            connection.execute(text("""
                UPDATE parameters
                SET unit = :unit,
                    is_3025_method = :is_method,
                    apha_24th_edition_method = :apha_method
                WHERE id = :id
            """), {
                "unit": row.get("Unit"),
                "is_method": row.get("IS 3025 Method"),
                "apha_method": row.get("APHA 24th Edition Method"),
                "id": param_id
            })
            updated += 1
        else:
            unmatched.append(row["Parameter"])

# Step 3: Save unmatched parameter names
pd.DataFrame(unmatched, columns=["Unmatched Parameter"]).to_csv("unmatched_parameters.csv", index=False)

# Step 4: Print summary
print("\n✅ Update Summary")
print(f"✔️  Updated rows: {updated}")
print(f"❌ Not found in DB: {len(unmatched)}")
print("📄 Unmatched names saved to: unmatched_parameters.csv")
