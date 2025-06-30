from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask import session

from config.db import verificar_base_datos_rostros
from controllers.registro_misas import registromisas_bp

app = Flask(__name__)
app.secret_key = '1234'
CORS(app)
@app.context_processor
def inject_user():
    return dict(user=session.get('usuario'))
# Registrar blueprints
app.register_blueprint(registromisas_bp)

#----

@app.route('/')
def home():
    return redirect(url_for('registromisas_bp.misas_por_fecha'))

if __name__ == '__main__':
    if verificar_base_datos_rostros():
        print("Iniciando servidor Flask...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("No se puede iniciar el servidor sin la base de datos de rostros.")
