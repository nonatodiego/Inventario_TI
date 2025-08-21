from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(255), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    setor = db.Column(db.String(100))
    nome_gestor = db.Column(db.String(255))
    localizacao = db.Column(db.String(100))
    desktop_notebook = db.Column(db.String(50))
    segunda_tela = db.Column(db.Boolean, default=False)
    licenca_office = db.Column(db.String(50))
    
    # Relacionamento com ativos
    assets = db.relationship('Asset', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.nome_usuario}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome_usuario': self.nome_usuario,
            'matricula': self.matricula,
            'setor': self.setor,
            'nome_gestor': self.nome_gestor,
            'localizacao': self.localizacao,
            'desktop_notebook': self.desktop_notebook,
            'segunda_tela': self.segunda_tela,
            'licenca_office': self.licenca_office,
            'assets': [asset.to_dict() for asset in self.assets] if self.assets else []
        }

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    celular_corporativo = db.Column(db.Boolean, default=False)
    headset = db.Column(db.Boolean, default=False)
    mouse_sem_fio = db.Column(db.Boolean, default=False)
    teclado_sem_fio = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Asset {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'celular_corporativo': self.celular_corporativo,
            'headset': self.headset,
            'mouse_sem_fio': self.mouse_sem_fio,
            'teclado_sem_fio': self.teclado_sem_fio
        }

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class AuthUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    
    role = db.relationship('Role', backref='auth_users')

    def __repr__(self):
        return f'<AuthUser {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role.to_dict() if self.role else None
        }
