import psycopg2

try:
    conn = psycopg2.connect("postgresql://postgres:hive%402025@localhost:5432/system_nyo")
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM ubicacion;")
    rows = cur.fetchall()
    
    print("## Locations (Ubicacion):")
    for row in rows:
        print(row)
        
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
