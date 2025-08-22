from flask import Blueprint, request, jsonify
from io import BytesIO
import pandas as pd
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

@users_bp.route('/import', methods=['POST'])
def import_from_sheet():
    """Importar usuários e ativos a partir de uma planilha (XLSX ou CSV).
    Espera um campo multipart chamado 'file'. Retorna um resumo da importação."""
    try:
        if 'file' not in request.files:
            return jsonify({'message': "Arquivo não enviado. Envie em 'file'"}), 400

        f = request.files['file']
        filename = (f.filename or '').lower()
        if not filename.endswith(('.xlsx', '.csv')):
            return jsonify({'message': 'Formato não suportado. Use .xlsx ou .csv'}), 400

        buffer = BytesIO(f.read())

        # Ler planilha
        if filename.endswith('.csv'):
            df = pd.read_csv(buffer)
        else:
            df = pd.read_excel(buffer)

        if df.empty:
            return jsonify({'message': 'Planilha vazia'}), 400

        # Mapear colunas (aceita variações comuns)
        cols = {c.strip(): c for c in df.columns if isinstance(c, str)}
        def pick(*options):
            for opt in options:
                if opt in cols:
                    return cols[opt]
            return None

        col_nome = pick('Nome do Usuário', 'nome_usuario', 'Nome')
        col_matricula = pick('Matrícula', 'matricula')
        col_setor = pick('Setor', 'setor')
        col_gestor = pick('Nome do Gestor', 'Gestor', 'nome_gestor')
        col_local = pick('Localização', 'localizacao')
        col_tipo = pick('Desktop / Notebook', 'desktop_notebook', 'Tipo')
        col_segunda = pick('Segunda Tela', 'segunda_tela')
        col_lic = pick('Licença de Office', 'licenca_office')
        col_cel = pick('Celular Corporativo', 'celular_corporativo')
        col_headset = pick('Headset', 'headset')
        col_mouse = pick('Mouse sem Fio', 'mouse_sem_fio', 'Mouse e teclado sem fio')
        col_teclado = pick('Teclado sem Fio', 'teclado_sem_fio', 'Mouse e teclado sem fio')

        required = [col_nome]
        if not all(required):
            return jsonify({'message': 'Coluna obrigatória ausente: Nome do Usuário'}), 400

        created = 0
        updated = 0
        skipped = 0
        errors = []

        for i, row in df.iterrows():
            try:
                nome_usuario = str(row[col_nome]).strip() if col_nome else None
                if not nome_usuario or nome_usuario.lower() in ('nan', 'none'):
                    skipped += 1
                    continue

                matricula = str(row[col_matricula]).strip() if col_matricula and not pd.isna(row[col_matricula]) else None

                # Booleans util (aceita Sim/Não, True/False, 1/0)
                def as_bool(v):
                    if pd.isna(v):
                        return False
                    s = str(v).strip().lower()
                    return s in ('sim', 'true', '1', 'x', 'yes')

                dados_user = {
                    'nome_usuario': nome_usuario,
                    'matricula': matricula or f"MAT{100000 + i}",
                    'setor': str(row[col_setor]).strip() if col_setor and not pd.isna(row[col_setor]) else None,
                    'nome_gestor': str(row[col_gestor]).strip() if col_gestor and not pd.isna(row[col_gestor]) else None,
                    'localizacao': str(row[col_local]).strip() if col_local and not pd.isna(row[col_local]) else None,
                    'desktop_notebook': str(row[col_tipo]).strip() if col_tipo and not pd.isna(row[col_tipo]) else None,
                    'segunda_tela': as_bool(row[col_segunda]) if col_segunda in df.columns else False,
                    'licenca_office': str(row[col_lic]).strip() if col_lic and not pd.isna(row[col_lic]) else None,
                }

                # upsert por matrícula se existir, senão por nome
                query = None
                if dados_user['matricula']:
                    query = User.query.filter_by(matricula=dados_user['matricula']).first()
                if not query:
                    query = User.query.filter_by(nome_usuario=dados_user['nome_usuario']).first()

                if query:
                    # atualizar
                    for k, v in dados_user.items():
                        setattr(query, k, v)
                    # atualizar/definir assets (assumimos um registro)
                    asset = query.assets[0] if query.assets else Asset(user_id=query.id)
                    asset.celular_corporativo = as_bool(row[col_cel]) if col_cel in df.columns else False
                    asset.headset = as_bool(row[col_headset]) if col_headset in df.columns else False
                    # se coluna combinada existir, usa para ambos quando colunas separadas não existem
                    combined = as_bool(row[col_mouse]) if (col_mouse and col_mouse == col_teclado and col_mouse in df.columns) else None
                    asset.mouse_sem_fio = (as_bool(row[col_mouse]) if (col_mouse in df.columns and combined is None) else (combined or False))
                    asset.teclado_sem_fio = (as_bool(row[col_teclado]) if (col_teclado in df.columns and combined is None) else (combined or False))
                    if not query.assets:
                        db.session.add(asset)
                    updated += 1
                else:
                    # criar
                    user = User(**dados_user)
                    db.session.add(user)
                    db.session.flush()
                    combined = as_bool(row[col_mouse]) if (col_mouse and col_mouse == col_teclado and col_mouse in df.columns) else None
                    asset = Asset(
                        user_id=user.id,
                        celular_corporativo=as_bool(row[col_cel]) if col_cel in df.columns else False,
                        headset=as_bool(row[col_headset]) if col_headset in df.columns else False,
                        mouse_sem_fio=(as_bool(row[col_mouse]) if (col_mouse in df.columns and combined is None) else (combined or False)),
                        teclado_sem_fio=(as_bool(row[col_teclado]) if (col_teclado in df.columns and combined is None) else (combined or False)),
                    )
                    db.session.add(asset)
                    created += 1

            except Exception as e:
                errors.append(f"linha {i+1}: {str(e)}")
        
        db.session.commit()

        return jsonify({
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'errors': errors,
            'total_rows': int(df.shape[0])
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({'message': 'Erro ao importar planilha'}), 500
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
