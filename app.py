from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask import session

from babel.dates import format_date
from datetime import datetime
import locale


from config.db import verificar_base_datos_rostros
from controllers.registro_misas import registromisas_bp
from controllers.registro_bautizos import registrobautizos_bp
from controllers.registro_matrimonios import registromatrimonios_bp

app = Flask(__name__)
app.secret_key = '1234'
CORS(app)
@app.context_processor
def inject_user():
    return dict(user=session.get('usuario'))
# Registrar blueprints
app.register_blueprint(registromisas_bp)
app.register_blueprint(registrobautizos_bp)
app.register_blueprint(registromatrimonios_bp)

@app.template_filter('formatear_fecha_es')
def formatear_fecha_es(fecha):
    return format_date(fecha, format='full', locale='es_ES')

#----

@app.route('/')
def home():
    return redirect(url_for('registromatrimonios_bp.registro_matrimonios'))

if __name__ == '__main__':
    if verificar_base_datos_rostros():
        print("Iniciando servidor Flask...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("No se puede iniciar el servidor sin la base de datos de rostros.")
