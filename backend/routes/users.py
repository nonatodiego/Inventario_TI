from flask import Blueprint, request, jsonify
from models import User, Asset, db
from sqlalchemy import or_, func

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    """Listar usuários com filtros opcionais e paginação"""
    try:
        # Parâmetros de filtro
        search = request.args.get('search', '')
        setor = request.args.get('setor', '')
        gestor = request.args.get('gestor', '')

        # Paginação
        try:
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 100))
            page = 1 if page < 1 else page
            page_size = 1 if page_size < 1 else page_size
        except ValueError:
            page, page_size = 1, 100

        query = User.query

        # Aplicar filtros
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    User.nome_usuario.ilike(like),
                    User.matricula.ilike(like),
                    User.setor.ilike(like)
                )
            )

        if setor:
            query = query.filter(User.setor == setor)

        if gestor:
            query = query.filter(User.nome_gestor == gestor)

        # Total para paginação
        total = query.count()

        # Ordenação opcional (por nome)
        query = query.order_by(User.nome_usuario.asc())

        # Aplicar paginação
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return jsonify({
            'items': [user.to_dict() for user in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }), 200

    except Exception as e:
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/users/stats', methods=['GET'])
def get_users_stats():
    """Estatísticas agregadas respeitando filtros"""
    try:
        search = request.args.get('search', '')
        setor = request.args.get('setor', '')
        gestor = request.args.get('gestor', '')

        base = User.query
        if search:
            like = f"%{search}%"
            base = base.filter(
                or_(
                    User.nome_usuario.ilike(like),
                    User.matricula.ilike(like),
                    User.setor.ilike(like)
                )
            )
        if setor:
            base = base.filter(User.setor == setor)
        if gestor:
            base = base.filter(User.nome_gestor == gestor)

        total = base.count()

        # Contagens booleanas via join com Asset
        # Para evitar N+1, usar subconsultas agregadas
        from models import Asset

        segunda_tela = base.filter(User.segunda_tela.is_(True)).count()

        # Ativos
        join_q = base.join(Asset, Asset.user_id == User.id, isouter=True)
        celulares = join_q.filter(Asset.celular_corporativo.is_(True)).count()
        headsets = join_q.filter(Asset.headset.is_(True)).count()

        # Tipos de equipamento
        desktops = base.filter(User.desktop_notebook == 'Desktop').count()
        notebooks = base.filter(User.desktop_notebook == 'Notebook').count()
        nao_informado = base.filter((User.desktop_notebook.is_(None)) | (User.desktop_notebook == '')).count()

        # Licenças
        o365_e1 = base.filter(User.licenca_office == 'O365 E1').count()
        o365_e3 = base.filter(User.licenca_office == 'O365 E3').count()
        office_2019 = base.filter(User.licenca_office == 'Office 2019').count()
        sem_licenca = base.filter((User.licenca_office.is_(None)) | (User.licenca_office == '')).count()

        return jsonify({
            'total': total,
            'segunda_tela': segunda_tela,
            'ativos': {
                'celulares': celulares,
                'headsets': headsets
            },
            'equipamentos': {
                'desktop': desktops,
                'notebook': notebooks,
                'nao_informado': nao_informado
            },
            'licencas': {
                'O365 E1': o365_e1,
                'O365 E3': o365_e3,
                'Office 2019': office_2019,
                'Sem licença': sem_licenca
            }
        }), 200
    except Exception:
        return jsonify({'message': 'Erro interno do servidor'}), 500

@users_bp.route('/users', methods=['POST'])
def create_user():
    """Criar novo usuário"""
    try:
        data = request.get_json()

        # Validações obrigatórias
        if not data.get('nome_usuario'):
            return jsonify({'message': 'Nome é obrigatório'}), 400

        # Normalizar matrícula vazia -> None
        matricula = (data.get('matricula') or '').strip()
        if matricula == '':
            matricula = None

        # Verificar se matrícula já existe
        if matricula and User.query.filter_by(matricula=matricula).first():
            return jsonify({'message': 'Matrícula já existe'}), 400

        # Criar usuário
        user = User(
            nome_usuario=data['nome_usuario'],
            matricula=matricula,
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

        # Normalizar matrícula vazia -> None
        new_matricula = (data.get('matricula') or '').strip()
        if new_matricula == '':
            new_matricula = None

        # Verificar se matrícula já existe (exceto para o próprio usuário)
        if new_matricula is not None and new_matricula != user.matricula:
            if User.query.filter_by(matricula=new_matricula).first():
                return jsonify({'message': 'Matrícula já existe'}), 400

        # Atualizar dados do usuário
        user.nome_usuario = data.get('nome_usuario', user.nome_usuario)
        user.matricula = new_matricula if 'matricula' in data else user.matricula
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
