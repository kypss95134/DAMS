import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='1234')
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS dams_db;")
    print("Database dams_db created successfully!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
