import os
import mysql.connector

try:
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "script"),
    )

except mysql.connector.Error as erro:
    print(f"ERRO ao conectar no banco: {erro}")
    exit()

cursor = db.cursor()
