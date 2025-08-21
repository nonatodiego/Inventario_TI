#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from werkzeug.security import generate_password_hash
from src.models.user import db, AuthUser, Role
from src.main import app

def create_auth_users():
    with app.app_context():
        # Criar roles se não existirem
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrador do sistema')
            db.session.add(admin_role)
        
        consulta_role = Role.query.filter_by(name='consulta').first()
        if not consulta_role:
            consulta_role = Role(name='consulta', description='Usuário de consulta')
            db.session.add(consulta_role)
        
        db.session.commit()
        
        # Criar usuário administrador
        admin_user = AuthUser.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = AuthUser(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id
            )
            db.session.add(admin_user)
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe.")
        
        # Criar usuário de consulta
        consulta_user = AuthUser.query.filter_by(username='consulta').first()
        if not consulta_user:
            consulta_user = AuthUser(
                username='consulta',
                password_hash=generate_password_hash('consulta123'),
                role_id=consulta_role.id
            )
            db.session.add(consulta_user)
            print("Usuário consulta criado com sucesso!")
        else:
            print("Usuário consulta já existe.")
        
        db.session.commit()
        print("Usuários de autenticação configurados com sucesso!")

if __name__ == '__main__':
    create_auth_users()

