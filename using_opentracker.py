import hashlib
import time
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import subprocess
import os
import signal
from urllib.parse import urlparse, parse_qs
import functools
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__, static_folder='./static/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///torrents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
opentracker_process = None

difficulty = '00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'  # hex of threshold
challenges = {}

acceptable_categories = ['catagory1', 'catagory2', 'catagory3', 'etc']

ADMIN_KEY = 'random_key' # change this

class Torrent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    info_hash = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    magnet_link = db.Column(db.Text)
    delete_key = db.Column(db.String(36), unique=True, nullable=False, default=str(uuid.uuid4()))

    def __repr__(self):
        return f'<Torrent {self.name}, {self.info_hash}>'
    
def require_admin_key(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('Admin-Key') != ADMIN_KEY:
            return jsonify({'message': 'Forbidden: Invalid admin key'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Try to send the requested file from the static folder
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # If the file does not exist, return the index.html
        return send_from_directory(app.static_folder, 'index.html')
    
@app.errorhandler(404)
def page_not_found(e):
    # Redirect to the main page
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/start', methods=['POST'])
@require_admin_key
def start_opentracker():
    global opentracker_process
    if opentracker_process is not None:
        return jsonify({'message': 'Opentracker is already running.'}), 400

    opentracker_executable = './opentracker'
    whitelist_file = './whitelist'
    opentracker_process = subprocess.Popen([opentracker_executable, '-w', whitelist_file])
    return jsonify({'message': 'Opentracker started.'})

@app.route('/stop', methods=['POST'])
@require_admin_key
def stop_opentracker():
    global opentracker_process
    if opentracker_process is None:
        return jsonify({'message': 'Opentracker is not running.'}), 400

    opentracker_process.send_signal(signal.SIGTERM)
    opentracker_process.wait()
    opentracker_process = None
    return jsonify({'message': 'Opentracker stopped.'})

@app.route('/reload', methods=['POST'])
@require_admin_key
def reload_opentracker():
    if opentracker_process is None:
        return jsonify({'message': 'Opentracker is not running.'}), 400

    os.kill(opentracker_process.pid, signal.SIGHUP)
    return jsonify({'message': 'Opentracker configuration reloaded.'})

@app.route('/update_torrent', methods=['POST'])
@require_admin_key
def update_torrent():
    global acceptable_categories
    data = request.json
    info_hash = data.get('info_hash')
    name = data.get('name')
    description = data.get('description')
    category = data.get('category')

    # Validate the input data
    if not info_hash:
        return jsonify({'message': 'Missing info_hash'}), 400
    if name is not None and not isinstance(name, str):
        return jsonify({'message': 'Invalid name format'}), 400
    if description is not None and not isinstance(description, str):
        return jsonify({'message': 'Invalid description format'}), 400
    if category is not None:
        if not isinstance(category, list) or not all(isinstance(cat, str) for cat in category):
            return jsonify({'message': 'Invalid category format'}), 400
        for cat in category:
            if cat not in acceptable_categories:
                return jsonify({'message': f'Invalid category: {cat}'}), 400
        category = ', '.join(category)

    # Find the torrent
    torrent = Torrent.query.filter_by(info_hash=info_hash).first()
    if not torrent:
        return jsonify({'message': 'Torrent not found'}), 404

    # Update the torrent details
    if name:
        torrent.name = name
    if description:
        torrent.description = description
    if category:
        torrent.category = category

    try:
        db.session.commit()
        return jsonify({'message': 'Torrent updated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating torrent', 'error': str(e)}), 500
    
@app.route('/admin-torrents', methods=['GET'])
@require_admin_key
def list_torrents_admin():
    torrents = Torrent.query.all()
    return jsonify([{
        'name': torrent.name,
        'info_hash': torrent.info_hash,
        'description': torrent.description,
        'category': torrent.category.split(', ') if torrent.category else [],
        'magnet_link': torrent.magnet_link,
        'delete_key': torrent.delete_key
    } for torrent in torrents])

@app.route('/add_torrent', methods=['POST'])
def add_torrent():
    global acceptable_categories
    data = request.json
    
    # Validate magnet_link
    magnet_link = data.get('magnet_link')
    if not magnet_link or not isinstance(magnet_link, str):
        return jsonify({'message': 'Invalid or missing magnet link.'}), 400

    # Validate description
    description = data.get('description', '')
    if not isinstance(description, str):
        return jsonify({'message': 'Invalid description.'}), 400

    # Validate categories
    categories = data.get('category', [])
    if not isinstance(categories, list) or not all(isinstance(cat, str) for cat in categories):
        return jsonify({'message': 'Invalid category format.'}), 400

    for cat in categories:
        if cat not in acceptable_categories:
            return jsonify({'message': f'Invalid category: {cat}'}), 400

    # Validate nonce
    nonce = data.get('nonce')
    if not nonce or not isinstance(nonce, int):
        return jsonify({'message': 'Invalid or missing nonce.'}), 400

    # Validate challenge
    challenge = data.get('challenge')
    if not challenge or not isinstance(challenge, str):
        return jsonify({'message': 'Invalid or missing challenge.'}), 400

    challenge_parts = challenge.split(':')
    if len(challenge_parts) != 2:
        return jsonify({'message': 'Invalid PoW challenge format.'}), 400

    challenge_str, challenge_timestamp = challenge_parts
    try:
        challenge_timestamp = int(challenge_timestamp)
    except ValueError:
        return jsonify({'message': 'Invalid PoW challenge timestamp.'}), 400

    current_time = int(time.time())
    
    # Check if the challenge is expired (e.g., older than 5 minutes)
    if current_time - challenge_timestamp > 300:
        return jsonify({'message': 'PoW challenge expired.'}), 400

    # Check if the challenge was already used
    if challenge not in challenges:
        return jsonify({'message': 'Invalid PoW challenge.'}), 400

    # Validate PoW
    if not validate_pow(challenge, nonce, difficulty):
        return jsonify({'message': 'Invalid PoW solution.'}), 400

    # Remove used challenge
    del challenges[challenge]

    category = ', '.join(categories)

    try:
        magnet_params = urlparse(magnet_link).query
        magnet_dict = parse_qs(magnet_params)
        info_hash = magnet_dict['xt'][0].split(':')[-1]
        name = magnet_dict.get('dn', [''])[0]
        trackers = magnet_dict.get('tr', [])
    except (IndexError, KeyError):
        return jsonify({'message': 'Invalid magnet link format.'}), 400

    if 'your.domain.com' not in [urlparse(tracker).hostname for tracker in trackers]:
        return jsonify({'message': 'Torrent not tracked by your.domain.com.'}), 400

    if not Torrent.query.filter_by(info_hash=info_hash).first():
        delete_key = str(uuid.uuid4())
        torrent = Torrent(
            name=name, 
            info_hash=info_hash, 
            description=description, 
            category=category, 
            magnet_link=magnet_link, 
            delete_key=delete_key
        )
        db.session.add(torrent)
        db.session.commit()
        with open('whitelist', 'a+') as file:
            file.write(info_hash + '\n')
        os.kill(opentracker_process.pid, signal.SIGHUP)
        return jsonify({'message': f'Torrent {name} added to tracking.', 'delete_key': delete_key}), 201
    
    return jsonify({'message': 'Torrent already tracked.'}), 409


@app.route('/pow-challenge', methods=['GET'])
def get_pow_challenge():
    challenge = os.urandom(16).hex()
    timestamp = int(time.time())
    challenge_with_timestamp = f"{challenge}:{timestamp}"
    challenges[challenge_with_timestamp] = timestamp
    return jsonify({'challenge': challenge_with_timestamp, 'threshold': difficulty})

@app.route('/torrents', methods=['GET'])
def list_torrents():
    torrents = Torrent.query.all()
    return jsonify([{
        'name': torrent.name,
        'info_hash': torrent.info_hash,
        'description': torrent.description,
        'category': torrent.category.split(', ') if torrent.category else [],
        'magnet_link': torrent.magnet_link
    } for torrent in torrents])

@app.route('/remove_torrent', methods=['DELETE'])
def remove_torrent():
    data = request.json
    info_hash = data.get('info_hash')
    delete_key = data.get('delete_key')
    torrent = Torrent.query.filter_by(info_hash=info_hash, delete_key=delete_key).first()
    
    if torrent:
        db.session.delete(torrent)
        db.session.commit()

        # Update the whitelist file
        update_whitelist_file()

        # Reload opentracker configuration
        if opentracker_process:
            os.kill(opentracker_process.pid, signal.SIGHUP)
        
        return jsonify({'message': f'Torrent {torrent.name} removed from tracking.'}), 200
    
    return jsonify({'message': 'Torrent not found or invalid delete key.'}), 404

def update_whitelist_file():
    """Recreate the whitelist file based on the current database entries."""
    torrents = Torrent.query.all()
    with open('whitelist', 'w') as file:
        for torrent in torrents:
            file.write(torrent.info_hash + '\n')

def validate_pow(challenge, nonce, threshold):
    attempt = f"{challenge}{nonce}".encode('utf-8')
    hash_attempt = hashlib.sha256(attempt).hexdigest()
    return int(hash_attempt, 16) < int(threshold, 16)

def start_opentracker_at_startup():
    global opentracker_process
    if opentracker_process is None:
        opentracker_executable = './opentracker'
        whitelist_file = './whitelist'
        opentracker_process = subprocess.Popen([opentracker_executable, '-w', whitelist_file])
        print('Opentracker started at startup.')

if __name__ == '__main__':
    start_opentracker_at_startup()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
