from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import torch
from datetime import datetime
import subprocess
from geopy.geocoders import Nominatim
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Simplified Waste Category Mapping (Recyclable, Compostable, General Waste)
waste_map = {
    # Compostable items
    "banana": "Compostable",
    "apple": "Compostable",
    "orange": "Compostable",
    "carrot": "Compostable",
    "potted plant": "Compostable",
    "sandwich": "Compostable",
    "broccoli": "Compostable",
    "carrot": "Compostable",

    # Recyclable items
    "bottle": "Recyclable",
    "cup": "Recyclable",
    "wine glass": "Recyclable",
    "can": "Recyclable",
    "tin can": "Recyclable",
    "cardboard": "Recyclable",
    "book": "Recyclable",
    "vase": "Recyclable",

    # E-waste (considered recyclable)
    "cell phone": "Recyclable",
    "laptop": "Recyclable",
    "tv": "Recyclable",
    "remote": "Recyclable",
    "keyboard": "Recyclable",
    "mouse": "Recyclable",

    # Everything else defaults to general
}

# Suggested disposal messages per category
disposal_message = {
    "Recyclable": "Place this item in the recycling bin.",
    "Compostable": "Place this item in the compost/organic waste bin.",
    "General": "Place this item in the general waste bin."
}

# Database Models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class WasteLocation(db.Model):
    __tablename__ = 'waste_location'
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('locations', lazy=True))

with app.app_context():
    db.create_all()

# Upload folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('smart_waste.html')

@app.route('/index')
def index():
    if 'user_id' in session:
        return redirect(url_for('detect_waste'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_pw)

        if role == 'admin':
            new_user.is_admin = True

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin

            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('detect_waste'))

        flash('Invalid login!', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

# Waste Detection Route
@app.route('/detect', methods=['GET', 'POST'])
def detect_waste():
    if 'user_id' not in session:
        flash("Please log in first!", 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            flash("No file uploaded!", "danger")
            return redirect(url_for('detect_waste'))

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Run YOLOv5
        results = model(file_path)
        predictions = results.pandas().xyxy[0]

        output = []

        if not predictions.empty:
            for _, row in predictions.iterrows():
                label = row['name']
                confidence = row['confidence'] * 100

                # Simplified category
                category = waste_map.get(label, "General")
                suggestion = disposal_message[category]

                output.append({
                    "classification": label,
                    "category": category,
                    "confidence": f"{confidence:.2f}%",
                    "disposal": suggestion
                })

            image_url = url_for('static', filename=f'uploads/{file.filename}')
            return render_template('result.html', predictions=output, image_url=image_url)

        return render_template('result.html', predictions=[], image_url=None)

    return render_template('index.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    locations_raw = WasteLocation.query.all()

    # Convert ORM objects → dictionaries
    locations = [
        {
            "id": loc.id,
            "location_name": loc.location_name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "username": loc.user.username,
            "is_completed": loc.is_completed
        }
        for loc in locations_raw
    ]

    return render_template('admin_dashboard.html', locations=locations)


@app.route('/submit_location', methods=['POST'])
def submit_location():
    location_name = request.form.get('location')

    if not location_name:
        flash('Location name is required!', 'danger')
        return redirect(url_for('index'))

    geolocator = Nominatim(user_agent="smart-waste-app")

    try:
        location = geolocator.geocode(location_name)
        if location:
            new_loc = WasteLocation(
                location_name=location_name,
                latitude=location.latitude,
                longitude=location.longitude,
                user_id=session['user_id']
            )
            db.session.add(new_loc)
            db.session.commit()

            flash(f"Location '{location_name}' submitted successfully!", 'success')
        else:
            flash(f"Could not find location: {location_name}", 'danger')

    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')

    return redirect(url_for('admin_dashboard'))



@app.route('/delete_location/<int:location_id>', methods=['POST'])
def delete_location(location_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    loc = WasteLocation.query.get(location_id)

    if loc:
        db.session.delete(loc)
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/location_history')
def location_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    locations = WasteLocation.query.filter_by(user_id=user_id).all()

    return render_template('location_history.html', locations=locations)

if __name__ == "__main__":
    app.run(debug=True)
