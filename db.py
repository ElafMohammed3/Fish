import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "admin21"),
    "database": "fish_database",
    "port": int(os.getenv("DB_PORT", 3306)),
}


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
            charset="utf8mb4",
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


def init_tables():
    conn = get_db_connection()
    if conn is None:
        print("Unable to connect to DB, cannot initialize tables.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fish (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            image LONGBLOB,
            description TEXT,
            source_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        conn.commit()
        print("Created table 'fish' successfully.")
    except Error as e:
        print(f"An error occurred while creating the table: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()

def get_all_fish():
    conn = get_db_connection()
    fish_list = []
    if conn is None:
        return fish_list

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, description, source_url, image FROM fish ORDER BY name")
        fish_list = cursor.fetchall()
    except Error as e:
        print(f"Error fetching fish data: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()
    return fish_list

def search_fish(search_term):
    conn = get_db_connection()
    fish_list = []
    if conn is None:
        return fish_list
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, description, source_url, image FROM fish WHERE name LIKE %s OR description LIKE %s ORDER BY name"
        cursor.execute(query, ('%' + search_term + '%', '%' + search_term + '%'))
        fish_list = cursor.fetchall()
    except Error as e:
        print(f"Error searching fish: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()
    return fish_list

def add_new_fish(name, description, source_url, image_data=None):
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection error."
            
    try:
        cursor = conn.cursor()
        query = "INSERT INTO fish (name, description, source_url, image) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, description, source_url, image_data))
        conn.commit()
        return True, "Fish added successfully."
    except Error as e:
        if e.errno == 1062:
            return False, f"Fish with name '{name}' already exists."
        else:
            return False, f"Error: {e}"
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


if __name__ == "_main_":
    init_tables()