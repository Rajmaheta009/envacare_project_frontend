import json
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="envacare_project_zcld",
    user="envacare_project_zcld_user",
    password="LGcZvwBAS7UygLejyQfPkBwExXF4bZw6",
    port="8000"
)
cur = conn.cursor()

# Load data from JSON file
with open("test_for_extraconcept/output_data.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Insert into database
for item in data:
    cur.execute(
        "INSERT INTO parameters (name, parent_id, price) VALUES (%s, %s, %s)",
        (item['name'], item['parent_id'], item['price'])
    )

conn.commit()
cur.close()
conn.close()

print("✅ Data seeded successfully from output_data.json.")
