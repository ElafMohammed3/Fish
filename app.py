import os
import io
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
from mysql.connector import Error

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "database": os.getenv("DB_NAME", "FISH"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "secret_key_123")


def get_db_connection():
    """إنشاء اتصال جديد بقاعدة البيانات أو إرجاع None إذا فشل."""
    try:
        conn = mysql.connector.connect(**DB)
        return conn
    except Error as e:
        print("خطأ في الاتصال بقاعدة البيانات:", e)
        return None


def init_tables():
    """إنشاء جدول fish إذا لم يكن موجوداً."""
    conn = get_db_connection()
    if conn is None:
        print("فشل إنشاء الجداول لأن الاتصال بالقاعدة فشل.")
        return
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fish (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                source_url VARCHAR(2083),
                image LONGBLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
    except Error as e:
        print("خطأ أثناء init_tables:", e)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_all_fish():
    """إرجاع قائمة الأسماك كقوائم من القواميس (بدون الصورة لاقتصاد الذاكرة)."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, description, source_url, created_at FROM fish ORDER BY id DESC")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print("خطأ في get_all_fish:", e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def search_fish(term):
    """بحث في الاسم والوصف، يعيد قائمة قواميس."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        like = f"%{term}%"
        cursor.execute("""
            SELECT id, name, description, source_url, created_at
            FROM fish
            WHERE name LIKE %s OR description LIKE %s
            ORDER BY id DESC
        """, (like, like))
        return cursor.fetchall()
    except Error as e:
        print("خطأ في search_fish:", e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def add_new_fish(name, description, source_url, image_data):
    """إدراج سمكة جديدة. يرجع (True, last_id) أو (False, error_message)."""
    conn = get_db_connection()
    if conn is None:
        return False, "فشل الاتصال بقاعدة البيانات"
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO fish (name, description, source_url, image) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, description, source_url, image_data))
        conn.commit()
        last_id = cursor.lastrowid
        return True, last_id
    except Error as e:
        print("خطأ في add_new_fish:", e)
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


with app.app_context():
    init_tables()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/image/<int:fish_id>')
def get_image(fish_id):
    conn = get_db_connection()
    if conn is None:
        return "Error", 500

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM fish WHERE id = %s", (fish_id,))
        result = cursor.fetchone()

        if result and result[0]:
            return send_file(io.BytesIO(result[0]), mimetype='image/jpeg')
        else:
            return "No image", 404
    except Error as e:
        print(f"Error fetching image: {e}")
        return "Error", 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/fish')
def fish_list():
    fish = get_all_fish()
    return render_template("fish_list.html", fish_list=fish)


@app.route('/search')
def search_fish_route():
    search_term = request.args.get('q', '')
    if search_term:
        fish = search_fish(search_term)
    else:
        fish = get_all_fish()
    return render_template("fish_list.html", fish_list=fish, search_term=search_term)


@app.route('/add', methods=['GET', 'POST'])
def add_fish():
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        source_url = request.form.get("source_url")
        image = request.files.get("image")

        image_data = None
        if image and image.filename != '':
            image_data = image.read()

        if not name:
            flash("يجب إدخال اسم السمكة", "error")
            return redirect(url_for('add_fish'))

        success, message = add_new_fish(name, description, source_url, image_data)

        if success:
            flash(f"تم إضافة {name}", "success")
            return redirect(url_for("fish_list"))
        else:
            flash(f"فشل: {message}", "error")
            return redirect(url_for('add_fish'))

    return render_template("add_fish.html")


if __name__ == '__main__':
    app.run(debug=True)