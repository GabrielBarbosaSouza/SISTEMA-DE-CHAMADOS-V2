import os
import mysql.connector

try:
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "script"),
        ssl_disabled=os.environ.get("DB_SSL_DISABLED", "true").lower() == "true",
    )

except mysql.connector.Error as erro:
    print(f"ERRO ao conectar no banco: {erro}")
    exit()

cursor = db.cursor()