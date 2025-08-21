import os
import sys
import pandas as pd

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from src.models.user import db, User, Asset, Role, AuthUser
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def populate_database():
    app = create_app()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Criar roles padrão
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
        
        consulta_role = Role.query.filter_by(name='consulta').first()
        if not consulta_role:
            consulta_role = Role(name='consulta')
            db.session.add(consulta_role)
        
        db.session.commit()
        
        # Criar usuários de autenticação padrão
        admin_user = AuthUser.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = AuthUser(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id
            )
            db.session.add(admin_user)
        
        consulta_user = AuthUser.query.filter_by(username='consulta').first()
        if not consulta_user:
            consulta_user = AuthUser(
                username='consulta',
                password_hash=generate_password_hash('consulta123'),
                role_id=consulta_role.id
            )
            db.session.add(consulta_user)
        
        db.session.commit()
        
        # Carregar dados da planilha
        excel_file = '/home/ubuntu/upload/Planilha_Ativos_TI.xlsx'
        df = pd.read_excel(excel_file)
        
        print(f"Carregando {len(df)} registros da planilha...")
        
        for index, row in df.iterrows():
            # Verificar se o usuário já existe
            existing_user = User.query.filter_by(nome_usuario=row['Nome do Usuário']).first()
            if existing_user:
                print(f"Usuário {row['Nome do Usuário']} já existe, pulando...")
                continue
            
            # Criar usuário
            user = User(
                nome_usuario=row['Nome do Usuário'],
                matricula=f"MAT{1000 + index}",  # Gerar matrícula fictícia
                setor=row['Setor'],
                nome_gestor=row['Nome do Gestor'],
                localizacao=row['Localização'],
                desktop_notebook=row['Desktop / Notebook'],
                segunda_tela=row['Segunda Tela'] == 'Sim',
                licenca_office=row['Licença de Office']
            )
            
            db.session.add(user)
            db.session.flush()  # Para obter o ID do usuário
            
            # Criar ativos
            asset = Asset(
                user_id=user.id,
                celular_corporativo=row['Celular Corporativo'] == 'Sim',
                headset=row['Headset'] == 'Sim',
                mouse_sem_fio=row['Mouse e teclado sem fio'] == 'Sim',
                teclado_sem_fio=row['Mouse e teclado sem fio'] == 'Sim'  # Assumindo que mouse e teclado são juntos
            )
            
            db.session.add(asset)
            
            print(f"Adicionado: {row['Nome do Usuário']}")
        
        db.session.commit()
        print("Banco de dados populado com sucesso!")
        print(f"Total de usuários: {User.query.count()}")
        print(f"Total de ativos: {Asset.query.count()}")

if __name__ == '__main__':
    populate_database()

