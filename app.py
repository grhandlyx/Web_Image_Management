"""Main Flask application for Image Drive system"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import secrets
import hashlib
import json
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from config import Config
import time
from datetime import timezone



# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Image Drive startup')

def monitor_latency(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time

                perf_log = PerformanceLog(
                    operation_type=operation_name,
                    latency=latency,
                    user_id=session.get('user_id'),
                    details=json.dumps({'status': 'success'})
                )
                db.session.add(perf_log)
                db.session.commit()

                app.logger.info(f'PERF_MONITOR - {operation_name}: {latency:.4f}s')
                return result
            except Exception as e:
                latency = time.time() - start_time
                app.logger.error(f'PERF_ERROR - {operation_name}: {latency:.4f}s, Error: {str(e)}')
                raise
        return wrapper
    return decorator


# Inject static file version into all templates
@app.context_processor
def inject_static_version():
    return {'static_version': app.config['STATIC_VERSION']}

# Disable caching for static files in development
@app.after_request
def add_header(response):
    if app.debug or app.config.get('ENV') == 'development':
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# Database Models
class User(db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))
    ocr_text = db.Column(db.Text)
    embedding = db.Column(db.Text)  # Store as JSON
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)

class SearchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_type = db.Column(db.String(50))
    query = db.Column(db.String(512))
    results_count = db.Column(db.Integer)
    topk_results = db.Column(db.Text)
    ocr_results = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PerformanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)  
    latency = db.Column(db.Float, nullable=False)  
    details = db.Column(db.Text)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        user_session = Session.query.filter_by(token=token).first()
        if not user_session or user_session.expires_at < datetime.utcnow():
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'token' in session:
        return redirect(url_for('gallery'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        app.logger.info(f'New user registered: {username}')
        return redirect(url_for('login', registered='true'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid username or password')
        token = secrets.token_hex(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        user_session = Session(user_id=user.id, token=token, expires_at=expires_at)
        db.session.add(user_session)
        db.session.commit()
        session['token'] = token
        session['user_id'] = user.id
        session['username'] = user.username
        app.logger.info(f'User logged in: {username}')
        return redirect(url_for('gallery'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    token = session.get('token')
    if token:
        user_session = Session.query.filter_by(token=token).first()
        if user_session:
            db.session.delete(user_session)
            db.session.commit()
    session.clear()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
@monitor_latency('image_upload')

def upload():
    from utils import compute_clip_embedding, extract_ocr_text, auto_categorize_image, allowed_file
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    try:
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        existing_image = Image.query.filter_by(file_hash=file_hash).first()
        if existing_image:
            return jsonify({'error': 'Duplicate image', 'image_id': existing_image.id}), 409
        filename = secure_filename(file.filename)
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        embedding = compute_clip_embedding(file_path)
        ocr_text = extract_ocr_text(file_path)
        category = auto_categorize_image(file_path)
        image = Image(filename=unique_filename, original_filename=filename, file_path=file_path,
                     file_hash=file_hash, file_size=len(file_content), embedding=json.dumps(embedding.tolist()),
                     ocr_text=ocr_text, category=category, user_id=session['user_id'])
        db.session.add(image)
        db.session.commit()
        app.logger.info(f'Image uploaded: {filename}')
        return jsonify({'success': True, 'image_id': image.id, 'category': category}), 201
    except Exception as e:
        app.logger.error(f'Upload error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/gallery')
@login_required
def gallery():
    page = request.args.get('page', 1, type=int)
    images = Image.query.order_by(Image.upload_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('gallery.html', images=images)

@app.route('/image/<int:image_id>')
@login_required
def image_detail(image_id):
    from utils import find_similar_images
    image = Image.query.get_or_404(image_id)
    similar_images = find_similar_images(image.id, limit=6)
    return render_template('detail.html', image=image, similar_images=similar_images)

@app.route('/download/<int:image_id>')
@login_required
def download_image(image_id):
    image = Image.query.get_or_404(image_id)
    image.download_count += 1
    db.session.commit()
    app.logger.info(f'Image downloaded: {image.filename}')
    return send_file(image.file_path, as_attachment=True, download_name=image.original_filename)

@app.route('/serve/<int:image_id>')
@login_required
def serve_image(image_id):
    image = Image.query.get_or_404(image_id)
    return send_file(image.file_path)

@app.route('/search/text')
@login_required
@monitor_latency('text_search')
def search_text():
    from utils import search_by_text
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    try:
        results = search_by_text(query)
        topk_list = [{"image_id": img.id, "similarity": float(score)} for img, score in results]
        search_log = SearchLog(user_id=session['user_id'], search_type='text', query=query, results_count=len(results),
                               topk_results=json.dumps(topk_list))
        db.session.add(search_log)
        db.session.commit()

        return jsonify({'results': [{'id': img.id, 'filename': img.original_filename,
                                    'similarity': float(score)} for img, score in results]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search/ocr')
@login_required
@monitor_latency('ocr_search')
def search_ocr():
    from utils import search_by_ocr
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    try:
        results = search_by_ocr(query)
        ocr_list = [img.id for img in results]
        search_log = SearchLog(user_id=session['user_id'], search_type='ocr', query=query, results_count=len(results),
                               ocr_results=json.dumps(ocr_list))
        db.session.add(search_log)
        db.session.commit()
        return jsonify({'results': [{'id': img.id, 'filename': img.original_filename,
                                    'ocr_text': img.ocr_text[:200]} for img in results]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search/similar', methods=['POST'])
@login_required
@monitor_latency('similarity_search')
def search_similar():
    from utils import compute_clip_embedding, find_similar_images
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    try:
        temp_path = os.path.join(app.config['TEMP_FOLDER'], f"temp_{secrets.token_hex(8)}_{secure_filename(file.filename)}")
        file.save(temp_path)
        embedding = compute_clip_embedding(temp_path)
        results = find_similar_images(embedding=embedding, limit=10)
        os.remove(temp_path)
        topk_list = [{"image_id": img.id, "similarity": float(score)} for img, score in results]
        search_log = SearchLog(user_id=session['user_id'], search_type='similarity', query=file.filename, results_count=len(results),
                               topk_results=json.dumps(topk_list))
        db.session.add(search_log)
        db.session.commit()

        return jsonify({'results': [{'id': img.id, 'filename': img.original_filename,
                                    'similarity': float(score)} for img, score in results]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search/online')
@login_required
@monitor_latency('online_search')
def search_online():
    """Search for images in online databases (Unsplash, Pexels, etc.)"""
    from online_search import search_online_images, is_online_search_available

    if not app.config.get('ENABLE_ONLINE_SEARCH'):
        return jsonify({'error': 'Online search is disabled'}), 403

    if not is_online_search_available():
        return jsonify({
            'error': 'Online search not configured. Please add API keys.',
            'help_url': '/help/online-search'
        }), 503

    query = request.args.get('q', '')
    provider = request.args.get('provider', 'auto')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        limit = app.config.get('ONLINE_SEARCH_LIMIT', 20)
        results = search_online_images(query, provider=provider, limit=limit)

        # Log the search
        search_log = SearchLog(
            user_id=session['user_id'],
            search_type='online',
            query=query,
            results_count=len(results)
        )
        db.session.add(search_log)
        db.session.commit()

        return jsonify({
            'results': results,
            'count': len(results),
            'provider': provider,
            'query': query
        })
    except Exception as e:
        app.logger.error(f'Online search error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/search/hybrid')
@login_required
@monitor_latency('hybrid_search')
def search_hybrid():
    from utils import search_by_text
    from online_search import search_online_images, is_online_search_available

    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Search locally
        local_results = search_by_text(query, limit=10)
        local_formatted = [{
            'id': img.id,
            'filename': img.original_filename,
            'similarity': float(score),
            'source': 'local',
            'url': url_for('serve_image', image_id=img.id),
            'detail_url': url_for('image_detail', image_id=img.id)
        } for img, score in local_results]

        # Search online if available
        online_results = []
        if app.config.get('ENABLE_ONLINE_SEARCH') and is_online_search_available():
            online_results = search_online_images(query, limit=10)

        topk_list = [{"image_id": img.id, "similarity": float(score)} for img, score in local_results]

        # Log the search
        search_log = SearchLog(
            user_id=session['user_id'],
            search_type='hybrid',
            query=query,
            results_count=len(local_formatted) + len(online_results),
            topk_results=json.dumps(topk_list)
        )
        db.session.add(search_log)
        db.session.commit()

        return jsonify({
            'local': local_formatted,
            'online': online_results,
            'query': query
        })
    except Exception as e:
        app.logger.error(f'Hybrid search error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
@login_required
def analytics():
    from utils import get_analytics_data
    data = get_analytics_data()
    return render_template('analytics.html', data=data)

@app.route('/analytics/export')
@login_required
def export_analytics():
    from utils import get_analytics_data
    import csv, io
    format_type = request.args.get('format', 'json')
    data = get_analytics_data()
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Category', 'Count'])
        for cat, count in data['category_distribution'].items():
            writer.writerow([cat, count])
        return app.response_class(response=output.getvalue(), mimetype='text/csv',
                                 headers={'Content-Disposition': 'attachment;filename=analytics.csv'})
    else:
        return app.response_class(response=json.dumps(data, indent=2), mimetype='application/json',
                                headers={'Content-Disposition': 'attachment;filename=analytics.json'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
