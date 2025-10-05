import oracledb

# Initialize Oracle client
oracledb.init_oracle_client(lib_dir=r"D:\orcale\instantclient_23_9")

try:
    print("Connecting to database...")
    conn = oracledb.connect(
        user="system",
        password="thaksin",
        dsn="localhost/XEPDB1"
    )
    cur = conn.cursor()

    # --- User input for email ---
    email = input("Enter an email address: ").strip()

    if "@" not in email:
        print("Invalid email format! Please include '@' symbol.")
    else:
        # Extract domain part
        domain = email.split("@")[1].lower()
        print(f"Extracted domain: {domain}")

        # --- Check if domain exists in the table ---
        cur.execute("SELECT domain_id FROM email_domains WHERE domain_name = :1", (domain,))
        row = cur.fetchone()

        if row:
            print(f"❌ Unsafe domain: '{domain}' (exists in blocked list)")
        else:
            print(f"✅ Safe domain: '{domain}' (not found in blocked list)")

except Exception as e:
    print("Error:", e)

finally:
    if 'cur' in locals() and cur:
        cur.close()
    if 'conn' in locals() and conn:
        conn.close()
    print("\nConnection closed.")
