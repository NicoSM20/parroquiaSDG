from flask import Blueprint, render_template, jsonify
from config.db import get_connection

visualizacion_bp = Blueprint('visualizacion_bp', __name__)

@visualizacion_bp.route('/')
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Llamada al procedimiento almacenado para obtener las plantas activas
        cursor.execute("""select * from vta_plantas_activas order by nombreCientifico asc""")
        rows = cursor.fetchall()
        resultado = [{'idPlanta': r[0], 'nombreCientifico': r[1], 'linkImagen': r[2], 'nomFamilia': r[3], 'nombres_comunes': r[4] or ''} for r in rows]
        return render_template('registrobautizo.html', plantas=resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


