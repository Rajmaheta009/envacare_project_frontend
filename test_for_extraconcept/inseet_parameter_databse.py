import psycopg2
import re

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="envacare_project",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def clean_text(text):
    text = text.replace("“", "").replace("”", "").replace("\"", "")
    text = re.sub(r"[=]+$", "", text).strip()
    return text.strip()

# Read input file
with open("Untitled-2.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

output_data = []
parent_stack = []  # Stack of (level, id)
id_counter = 1     # Used for internal hierarchy tracking, not DB

for line in lines:
    original_line = line.rstrip('\n')
    if not original_line.strip():
        continue

    # Normalize indentation
    line_expanded = original_line.replace("\t", "    ")
    leading_spaces = len(line_expanded) - len(line_expanded.lstrip(' '))
    level = leading_spaces // 4

    # Extract name and price
    if "====" in line_expanded:
        name, price = line_expanded.rsplit("====", 1)
        name = clean_text(name)
        price = price.strip().replace("=", "").strip()
    else:
        name = clean_text(line_expanded.strip())
        price = ""

    # Adjust parent stack
    while parent_stack and parent_stack[-1][0] >= level:
        parent_stack.pop()

    parent_id = parent_stack[-1][1] if parent_stack else None

    record = {
        "id": id_counter,
        "name": name,
        "parent_id": parent_id,
        "price": price if price else None
    }
    output_data.append(record)

    # Treat this as a parent category if there's no price
    if not price:
        parent_stack.append((level, id_counter))

    id_counter += 1

# Insert into services table
for item in output_data:
    cur.execute(
        "INSERT INTO parameters (name, parent_id, price) VALUES (%s, %s, %s)",
        (item['name'], item['parent_id'], item['price'])
    )

# Finalize
conn.commit()
cur.close()
conn.close()
