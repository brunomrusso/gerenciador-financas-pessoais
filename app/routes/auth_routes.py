import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from app import db
from app.models import User
from app.utils.mailer import send_password_reset

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já cadastrado'}), 409
    
    user = User(email=data['email'], nome=(data.get('nome') or '').strip() or None)
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Usuário criado com sucesso',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Email ou senha inválidos'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict()), 200


@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404
    data = request.get_json() or {}

    # Atualizar nome
    if 'nome' in data:
        user.nome = (data.get('nome') or '').strip() or None

    # Trocar senha (exige senha atual)
    new_password = data.get('new_password')
    if new_password:
        current = data.get('current_password') or ''
        if not user.check_password(current):
            return jsonify({'error': 'Senha atual incorreta'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'Nova senha deve ter ao menos 6 caracteres'}), 400
        user.set_password(new_password)

    db.session.commit()
    return jsonify(user.to_dict()), 200


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    # Resposta sempre 200 para nao vazar existencia de email
    if not email:
        return jsonify({'message': 'Se o email estiver cadastrado, voce recebera instrucoes'}), 200

    user = User.query.filter_by(email=email).first()
    if user:
        # Token JWT curto com purpose=reset
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=15),
            additional_claims={'purpose': 'password_reset'}
        )
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173').rstrip('/')
        link = f'{frontend_url}/reset?token={token}'
        try:
            send_password_reset(user.email, link, user.nome or '')
        except Exception as e:
            print(f'[forgot_password] erro envio: {e}')

    return jsonify({'message': 'Se o email estiver cadastrado, voce recebera instrucoes'}), 200


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('new_password') or ''

    if not token or len(new_password) < 6:
        return jsonify({'error': 'Dados invalidos (senha minima 6 caracteres)'}), 400

    try:
        decoded = decode_token(token)
    except Exception:
        return jsonify({'error': 'Token invalido ou expirado'}), 400

    if decoded.get('purpose') != 'password_reset':
        return jsonify({'error': 'Token nao autorizado'}), 400

    user_id = int(decoded.get('sub') or 0)
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario nao encontrado'}), 404

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Senha redefinida com sucesso'}), 200
