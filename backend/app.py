from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurações
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Importar modelos e rotas
from models import User, Asset
from routes.users import users_bp
from routes.export import export_bp

# Registrar blueprints
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/api/export')

# Garantir que as tabelas existam também quando rodando via gunicorn (produção)
with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
