import pandas as pd
import streamlit as st
import psycopg2
import re
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def insert_parameter_in_database():
    try:
        # PostgreSQL connection
        conn = psycopg2.connect(f'{DATABASE_URL}')
        cur = conn.cursor()

        def clean_text(text):
            text = text.replace("“", "").replace("”", "").replace("\"", "")
            text = re.sub(r"[=]+$", "", text).strip()
            return text.strip()

        # Read input file
        with open("perameter_add_in_database_shoertcut/Untitled-2.txt", "r", encoding="utf-8") as file:
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
                "price": price if price else None,
                "is_delete": False
            }
            output_data.append(record)

            # Treat this as a parent category if there's no price
            if not price:
                parent_stack.append((level, id_counter))

            id_counter += 1

        # Save to JSON file
        # with open("output_data.json", "w", encoding="utf-8") as json_file:
        #     json.dump(output_data, json_file, ensure_ascii=False, indent=4)

        # print("Data has been saved to output_data.json")

        # Truncate table before insertion (if required)
        cur.execute("TRUNCATE TABLE parameters RESTART IDENTITY CASCADE;")

        # Insert into parameters table
        for item in output_data:
            cur.execute(
                "INSERT INTO parameters (name, parent_id, price,is_delete) VALUES (%s, %s, %s,%s)",
                (item['name'], item['parent_id'], item['price'],item['is_delete'])
            )

        conn.commit()

        st.success("✅ All data has been successfully added to the database.")

        # Fetch and display all data from parameters table
        cur.execute("SELECT id, name, parent_id, price FROM parameters ORDER BY id")
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=["ID", "Name", "Parent ID", "Price","is_delete"])

        st.subheader("📋 Parameters Table")
        st.dataframe(df)

        # Close connections
        cur.close()
        conn.close()

    except Exception as e:
        st.warning(f"❌ Something went wrong: {e}")


# if __name__ == "__main__":
#     insert_parameter_in_database()