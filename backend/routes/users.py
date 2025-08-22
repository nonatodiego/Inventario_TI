from flask import Blueprint, request, jsonify
from models import User, Asset, db
from sqlalchemy import or_

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    """Listar todos os usuários com filtros opcionais"""
    try:
        # Parâmetros de filtro
        search = request.args.get('search', '')
        setor = request.args.get('setor', '')
        gestor = request.args.get('gestor', '')

        query = User.query

        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    User.nome_usuario.ilike(f'%{search}%'),
                    User.matricula.ilike(f'%{search}%'),
                    User.setor.ilike(f'%{search}%')
                )
            )

        if setor:
            query = query.filter(User.setor == setor)

        if gestor:
            query = query.filter(User.nome_gestor == gestor)

        users = query.all()
        return jsonify([user.to_dict() for user in users]), 200

    except Exception as e:
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/users', methods=['POST'])
def create_user():
    """Criar novo usuário"""
    try:
        data = request.get_json()

        # Validações obrigatórias
        if not data.get('nome_usuario') or not data.get('matricula'):
            return jsonify({'message': 'Nome e matrícula são obrigatórios'}), 400

        # Verificar se matrícula já existe
        if User.query.filter_by(matricula=data['matricula']).first():
            return jsonify({'message': 'Matrícula já existe'}), 400

        # Criar usuário
        user = User(
            nome_usuario=data['nome_usuario'],
            matricula=data['matricula'],
            setor=data.get('setor'),
            nome_gestor=data.get('nome_gestor'),
            localizacao=data.get('localizacao'),
            desktop_notebook=data.get('desktop_notebook'),
            segunda_tela=data.get('segunda_tela', False),
            licenca_office=data.get('licenca_office')
        )

        db.session.add(user)
        db.session.flush()  # Para obter o ID do usuário

        # Criar ativos associados
        asset = Asset(
            user_id=user.id,
            celular_corporativo=data.get('celular_corporativo', False),
            headset=data.get('headset', False),
            mouse_sem_fio=data.get('mouse_sem_fio', False),
            teclado_sem_fio=data.get('teclado_sem_fio', False)
        )

        db.session.add(asset)
        db.session.commit()

        return jsonify(user.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualizar usuário"""
    try:

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # Verificar se matrícula já existe (exceto para o próprio usuário)
        if data.get('matricula') and data['matricula'] != user.matricula:
            if User.query.filter_by(matricula=data['matricula']).first():
                return jsonify({'message': 'Matrícula já existe'}), 400

        # Atualizar dados do usuário
        user.nome_usuario = data.get('nome_usuario', user.nome_usuario)
        user.matricula = data.get('matricula', user.matricula)
        user.setor = data.get('setor', user.setor)
        user.nome_gestor = data.get('nome_gestor', user.nome_gestor)
        user.localizacao = data.get('localizacao', user.localizacao)
        user.desktop_notebook = data.get('desktop_notebook', user.desktop_notebook)
        user.segunda_tela = data.get('segunda_tela', user.segunda_tela)
        user.licenca_office = data.get('licenca_office', user.licenca_office)

        # Atualizar ativos
        asset = user.assets[0] if user.assets else Asset(user_id=user.id)
        asset.celular_corporativo = data.get('celular_corporativo', asset.celular_corporativo)
        asset.headset = data.get('headset', asset.headset)
        asset.mouse_sem_fio = data.get('mouse_sem_fio', asset.mouse_sem_fio)
        asset.teclado_sem_fio = data.get('teclado_sem_fio', asset.teclado_sem_fio)

        if not user.assets:
            db.session.add(asset)

        db.session.commit()
        return jsonify(user.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/setores', methods=['GET'])
def get_setores():
    """Listar todos os setores únicos"""
    try:
        setores = db.session.query(User.setor).filter(User.setor.isnot(None)).distinct().all()
        return jsonify([setor[0] for setor in setores]), 200
    except Exception as e:
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/gestores', methods=['GET'])
def get_gestores():
    """Listar todos os gestores únicos"""
    try:
        gestores = db.session.query(User.nome_gestor).filter(User.nome_gestor.isnot(None)).distinct().all()
        return jsonify([gestor[0] for gestor in gestores]), 200
    except Exception as e:
        return jsonify({'message': 'Erro interno do servidor'}), 500
