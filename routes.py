from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import secrets
from models import db, Admin, Opportunity

bp = Blueprint('api', __name__, url_prefix='/api')
login_manager = LoginManager()

def init_login_manager(app):
    login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    if not all([full_name, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'Account already exists'}), 400

    hashed_pw = generate_password_hash(password, method='scrypt')
    new_admin = Admin(full_name=full_name, email=email, password_hash=hashed_pw)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Account created successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)

    user = Admin.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    login_user(user, remember=remember)
    return jsonify({'status': 'success', 'email': email}), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success', 'message': 'Logged out successfully'}), 200

@bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    user = Admin.query.filter_by(email=email).first()
    if user:
        reset_token = secrets.token_urlsafe(32)
        print(f"[RESET LINK] Generated for {email}: /reset_password/{reset_token}")

    return jsonify({'status': 'success', 'message': 'If the email is registered, a reset link has been sent.'}), 200

@bp.route('/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()
    output = []
    for op in ops:
        output.append({
            'id': op.id,
            'title': op.title,
            'duration': op.duration,
            'startDate': op.start_date,
            'description': op.description,
            'skills': op.skills,
            'category': op.category,
            'futureOpportunities': op.future_opportunities,
            'maxApplicants': op.max_applicants
        })
    return jsonify({'status': 'success', 'data': output}), 200

@bp.route('/opportunities', methods=['POST'])
@login_required
def add_opportunity():
    data = request.get_json()
    
    required_fields = ['title', 'duration', 'startDate', 'description', 'skills', 'category', 'futureOpportunities']
    if not all(data.get(f) for f in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    new_op = Opportunity(
        title=data['title'],
        duration=data['duration'],
        start_date=data['startDate'],
        description=data['description'],
        skills=data['skills'],
        category=data['category'],
        future_opportunities=data['futureOpportunities'],
        max_applicants=data.get('maxApplicants'),
        admin_id=current_user.id
    )
    db.session.add(new_op)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': {
            'id': new_op.id,
            'title': new_op.title,
            'duration': new_op.duration,
            'startDate': new_op.start_date,
            'description': new_op.description,
            'skills': new_op.skills,
            'category': new_op.category,
            'futureOpportunities': new_op.future_opportunities,
            'maxApplicants': new_op.max_applicants
        }
    }), 201

@bp.route('/opportunities/<int:id>', methods=['GET'])
@login_required
def get_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({'error': 'Opportunity not found'}), 404

    return jsonify({
        'status': 'success',
        'data': {
            'id': op.id,
            'title': op.title,
            'duration': op.duration,
            'startDate': op.start_date,
            'description': op.description,
            'skills': op.skills,
            'category': op.category,
            'futureOpportunities': op.future_opportunities,
            'maxApplicants': op.max_applicants
        }
    }), 200

@bp.route('/opportunities/<int:id>/edit', methods=['PUT'])
@login_required
def edit_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({'error': 'Opportunity not found'}), 404

    data = request.get_json()
    required_fields = ['title', 'duration', 'startDate', 'description', 'skills', 'category', 'futureOpportunities']
    if not all(data.get(f) for f in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    op.title = data['title']
    op.duration = data['duration']
    op.start_date = data['startDate']
    op.description = data['description']
    op.skills = data['skills']
    op.category = data['category']
    op.future_opportunities = data['futureOpportunities']
    op.max_applicants = data.get('maxApplicants')

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Opportunity updated'}), 200

@bp.route('/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({'error': 'Opportunity not found'}), 404

    db.session.delete(op)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Opportunity deleted'}), 200
