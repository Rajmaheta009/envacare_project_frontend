# # import psycopg2

# # Connect to PostgreSQL
# # conn = psycopg2.connect(
# #     dbname="your_database",
# #     user="your_user",
# #     password="your_password",
# #     host="your_host",
# #     port="your_port"
# # )
# # cursor = conn.cursor()

# # Read the TXT file
# with open("Untitled-2.txt", "r", encoding="utf-8") as file:
#     lines = file.readlines()

# parent_id_stack = []  # Track parent categories at different levels
# current_parent_id = None  # Track parent category ID


# # print(lines)
# for line in lines:
#     line = line.strip()

#     if not line:
#         continue  # Skip empty lines

#     level = (len(line) - len(line.lstrip())) // 4  # Determine indentation level

#     # Extract name and price if present
#     if "====" in line:
#         name, price = line.rsplit("====", 1)
#         price = price.strip().replace("=", "").strip()
#     else:
#         name, price = line, None  # Category with no price

#     # Adjust the parent stack based on indentation level
#     while len(parent_id_stack) > level:
#         parent_id_stack.pop()

#     parent_id = parent_id_stack[-1] if parent_id_stack else None

#     # Insert the record into PostgreSQL
#     # cursor.execute("INSERT INTO parameters (name, parent_id, price) VALUES (%s, %s, %s) RETURNING id", (name.strip(), parent_id, price))
#     new_id =0

#     if price is None:  # If it's a category (not a priced item), add it to stack
#         parent_id_stack.append(new_id)
#     else:
#         new_id += 1  # Increment the ID for the next item
#     print(new_id,name.strip(),price)

# # conn.commit()
# # # Commit & Close
# # cursor.close()
# # conn.close()
# # print("Data Inserted Successfully!")
import json

# Read the TXT file
with open("Untitled-2.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

parent_id_stack = []  # Track parent categories at different levels
current_parent_id = None  # Track parent category ID

output_data = []  # List to hold JSON data
id_counter = 1    # ID counter to simulate auto-increment primary key
id_map = {}       # Map to store name -> id for handling parent_id
parent_stack_ids = []  # Stack to track the hierarchy of ids

for line in lines:
    original_line = line
    line = line.rstrip()

    if not line.strip():
        continue  # Skip empty lines

    level = (len(original_line) - len(original_line.lstrip())) // 4  # Indentation level

    # Extract name and price if present
    if "====" in line:
        name, price = line.rsplit("====", 1)
        price = price.strip().replace("=", "").strip()
    else:
        name = line.strip()
        price = None

    # Adjust the parent stack based on current level
    while len(parent_stack_ids) > level:
        parent_stack_ids.pop()

    parent_id = parent_stack_ids[-1] if parent_stack_ids else None

    record = {
        "id": id_counter,
        "name": name.strip(),
        "parent_id": parent_id,
        "price": price
    }

    output_data.append(record)

    if price is None:  # It's a category
        parent_stack_ids.append(id_counter)

    id_counter += 1

# Print JSON formatted output
print(json.dumps(output_data, indent=4))
