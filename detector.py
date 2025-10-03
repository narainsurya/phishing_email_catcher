import oracledb

# Initialize Oracle client
oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\instantclient_21_19")

try:
    print("Connecting to database:")
    conn = oracledb.connect(
        user="system",
        password="surya007",
        dsn="localhost/xe"
    )
    cur = conn.cursor()

    # Read domains from file
    with open("data.txt", "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    print(f"Attempting to insert {len(domains)} domains using sequence...")

    inserted_count = 0
    for domain in domains:
        # Use sequence and insert only if domain does not exist
        cur.execute("""
            INSERT INTO email_domains (domain_id, domain_name, status)
            SELECT email_domains_seq.NEXTVAL, :1, 'safe' FROM dual
            WHERE NOT EXISTS (
                SELECT 1 FROM email_domains WHERE domain_name = :1
            )
        """, (domain,))
        if cur.rowcount > 0:
            inserted_count += 1

    conn.commit()
    print(f"Insertion completed. {inserted_count} new domains added.")

    # Fetch and display all rows
    cur.execute("SELECT domain_id, domain_name, status FROM email_domains ORDER BY domain_id")
    all_rows = cur.fetchall()
    for row in all_rows:
        print(row)

except Exception as e:
    print("Error:", e)

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
    print("\nConnection closed.")
