from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

DB_FILE = "database.db"
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.cli.command("init-db")
def init_db():
    import click
    conn = get_db_connection()
    with open("schema.sql") as f:
        conn.executescript(f.read())
    conn.close()
    click.echo("Database initialized.")

# Home route (optional, for testing)
@app.route("/")
def home():
    return jsonify({"message": "Backend running"}), 200

# Timeline API
@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM timeline ORDER BY date DESC').fetchall()
    conn.close()
    return jsonify([dict(e) for e in events])

@app.route('/api/timeline', methods=['POST'])
def add_event():
    title = request.form.get('title')
    description = request.form.get('description')
    date = request.form.get('date')
    image = request.files.get('image')

    image_url = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        image_url = f"/static/uploads/{filename}"

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO timeline (title, description, date, image_url) VALUES (?, ?, ?, ?)',
        (title, description, date, image_url)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Event added successfully!'})

@app.route('/api/timeline/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM timeline WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Event {event_id} deleted successfully!'})

# Future Plans API
@app.route('/api/futureplans', methods=['GET'])
def get_plans():
    conn = get_db_connection()
    plans = conn.execute('SELECT * FROM future_plans ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(p) for p in plans])

@app.route('/api/futureplans', methods=['POST'])
def add_plan():
    data = request.json
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO future_plans (plan, importance) VALUES (?, ?)',
        (data['plan'], data.get('importance', 0))
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Plan added successfully!'})

@app.route('/api/futureplans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM future_plans WHERE id = ?', (plan_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Plan {plan_id} deleted successfully!'})

if __name__ == '__main__':
    # Auto-create DB if it doesn't exist
    if not os.path.exists(DB_FILE):
        from click.testing import CliRunner
        runner = CliRunner()
        runner.invoke(init_db)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
