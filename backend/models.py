from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Modelo para usuários do inventário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    setor = db.Column(db.String(50))
    nome_gestor = db.Column(db.String(100))
    localizacao = db.Column(db.String(100))
    desktop_notebook = db.Column(db.String(20))  # 'Desktop' ou 'Notebook'
    segunda_tela = db.Column(db.Boolean, default=False)
    licenca_office = db.Column(db.String(20))  # 'O365 E1', 'O365 E3', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com ativos
    assets = db.relationship('Asset', backref='user', lazy=True, cascade='all, delete-orphan')

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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'assets': [asset.to_dict() for asset in self.assets]
        }

class Asset(db.Model):
    """Modelo para ativos dos usuários"""
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    celular_corporativo = db.Column(db.Boolean, default=False)
    headset = db.Column(db.Boolean, default=False)
    mouse_sem_fio = db.Column(db.Boolean, default=False)
    teclado_sem_fio = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'celular_corporativo': self.celular_corporativo,
            'headset': self.headset,
            'mouse_sem_fio': self.mouse_sem_fio,
            'teclado_sem_fio': self.teclado_sem_fio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
