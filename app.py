from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()
from routes.dashboard import dashboard_bp
from routes.autenticacao import autenticacao_bp
from routes.chamados import chamados_bp
from routes.usuarios import usuarios_bp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(dashboard_bp)
app.register_blueprint(autenticacao_bp)
app.register_blueprint(chamados_bp)
app.register_blueprint(usuarios_bp)

if __name__ == "__main__":
    app.run(debug=True)