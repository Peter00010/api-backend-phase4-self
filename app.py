from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, Note

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
CORS(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Authenticate user (example only, implement your own logic)
    if username != 'username' or password != 'password':
        return jsonify({"msg": "Invalid username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route('/notes', methods=['GET', 'POST'])
@jwt_required()
def notes():
    current_user = get_jwt_identity()
    if request.method == 'GET':
        notes = Note.query.all()
        return jsonify([note.to_dict() for note in notes]), 200

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return jsonify({"msg": "Title and content are required"}), 400

        note = Note(title=title, content=content, user_id=current_user)
        db.session.add(note)
        db.session.commit()
        return jsonify({"msg": "Note created successfully"}), 201

@app.route('/notes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def note_detail(id):
    current_user = get_jwt_identity()
    note = Note.query.get_or_404(id)

    if note.user_id != current_user:
        return jsonify({"msg": "You do not have permission to access this note"}), 403

    if request.method == 'GET':
        return jsonify(note.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return jsonify({"msg": "Title and content are required"}), 400

        note.title = title
        note.content = content
        db.session.commit()
        return jsonify({"msg": "Note updated successfully"}), 200

    if request.method == 'DELETE':
        db.session.delete(note)
        db.session.commit()
        return jsonify({"msg": "Note deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
