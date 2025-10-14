from flask import Flask, render_template, request, redirect, url_for, flash
from db import init_tables, get_all_fish, add_new_fish

app = Flask(__name__)
app.secret_key = 'secret_key_123'

with app.app_context():
    init_tables()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/fish')
def fish_list():
    fish = get_all_fish()
    return render_template("fish_list.html", fish_list=fish)

@app.route('/add', methods=['GET', 'POST'])
def add_fish():
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        source_url = request.form.get("source_url")
        
        if not name:
            flash("يجب إدخال اسم السمكة", "error")
            return redirect(url_for('add_fish'))

        success, message = add_new_fish(name, description, source_url)
            
        if success:
            flash(f"تم إضافة {name}", "success")
            return redirect(url_for("fish_list"))
        else:
            flash(f"فشل: {message}", "error")
            return redirect(url_for('add_fish'))

    return render_template("add_fish.html")

if __name__ == '__main__':
    app.run(debug=True)