from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from src.models.user import AuthUser, db
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Chave secreta para JWT (em produção, usar variável de ambiente)
JWT_SECRET = 'sua-chave-secreta-super-segura'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token inválido!'}), 401
        
        if not token:
            return jsonify({'message': 'Token é obrigatório!'}), 401
        
        try:
            # Decodificar o token
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = AuthUser.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'Token inválido!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role.name != 'admin':
            return jsonify({'message': 'Acesso negado! Apenas administradores.'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username e password são obrigatórios!'}), 400
    
    user = AuthUser.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        # Gerar token JWT
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role.name
            }
        })
    
    return jsonify({'message': 'Credenciais inválidas!'}), 401

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'valid': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'role': current_user.role.name
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # Em uma implementação mais robusta, você poderia adicionar o token a uma blacklist
    return jsonify({'message': 'Logout realizado com sucesso!'})

