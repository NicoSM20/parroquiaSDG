from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from config.db import get_connection
from datetime import datetime
import logging

registro_bautizos_bp = Blueprint('registro_bautizos_bp', __name__)

@registro_bautizos_bp.route("/registrar_bautizo", methods=["GET", "POST"])
def registrar_bautizo():
    mensaje = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Cargar datos para los combos
        cursor.execute("SELECT idiglesias, nomIglesia FROM vta_iglesias ORDER BY nomIglesia")
        iglesias = cursor.fetchall()
        
        cursor.execute("SELECT idAniosParroquial, nomAnioParroquial FROM aniosparroquial ORDER BY anio DESC")
        anos_parroquiales = cursor.fetchall()
        
        cursor.execute("SELECT idsacerdotes, nom FROM vta_sacerdotes ORDER BY nom")
        sacerdotes = cursor.fetchall()
        
    except Exception as e:
        print(f"Error cargando datos: {e}")
        iglesias = []
        anos_parroquiales = []
        sacerdotes = []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    
    if request.method == "POST":
        try:
            data = request.get_json()
            #print("DATOS RECIBIDOS EN FLASK:", data)
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Llamar al procedimiento almacenado para registrar bautizo
            cursor.callproc("gestionar_bautizo", [
                1,  # ev = insertar
                None,  # id_bautizo
                data.get('dni_bautizado'),
                data.get('dni_padre'),
                data.get('dni_madre'),
                data.get('dni_padrino'),
                data.get('dni_madrina'),
                data.get('partida'),
                data.get('fecha_bautizo'),
                int(data.get('iglesia')),
                int(data.get('ano_parroquial')),
                int(data.get('sacerdote'))
            ])
            
            # Leer la respuesta
            for result in cursor.stored_results():
                resultado = result.fetchall()
                if resultado:
                    mensaje = resultado[0]["respuesta"]
                else:
                    mensaje = "✅ Bautizo registrado exitosamente"
            
            conn.commit()
            
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"mensaje": mensaje})
                
        except Exception as e:
            mensaje = f"❌ Error al registrar bautizo: {str(e)}"
            logging.error(f"Error registrando bautizo: {e}")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"mensaje": mensaje})
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    return render_template("registrar_bautizo.html", 
                         mensaje=mensaje,
                         iglesias=iglesias,
                         anos_parroquiales=anos_parroquiales,
                         sacerdotes=sacerdotes)

@registro_bautizos_bp.route("/buscar_persona", methods=["POST"])
def buscar_persona():
    try:
        data = request.get_json()
        dni = data.get('dni')
        
        if not dni or len(dni) != 8:
            return jsonify({"encontrado": False, "error": "DNI inválido"})
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Llamar al procedimiento almacenado corregido
        cursor.callproc("buscar_persona2", [dni])
        
        persona = None
        for result in cursor.stored_results():
            results = result.fetchall()
            if results:
                persona = results[0]
        
        if persona:
            return jsonify({
                "encontrado": True,
                "persona": {
                    "dni": persona["dni"],
                    "nombres": persona["nombres"],
                    "apellido1": persona["apellido1"],
                    "apellido2": persona.get("apellido2", "")
                }
            })
        else:
            return jsonify({"encontrado": False})
            
    except Exception as e:
        logging.error(f"Error buscando persona: {e}")
        return jsonify({"encontrado": False, "error": str(e)})
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@registro_bautizos_bp.route("/registrar_persona", methods=["POST"])
def registrar_persona():
    try:
        data = request.get_json()
        
        if not all([data.get('dni'), data.get('nombres'), data.get('apellido1'), data.get('genero')]):
            return jsonify({"exito": False, "mensaje": "Faltan datos requeridos"})
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.callproc("registrar_persona", [
            data.get('dni'),
            data.get('nombres'),
            data.get('apellido1'),
            data.get('apellido2', ''),
            data.get('genero')
        ])
        
        mensaje = "✅ Persona registrada exitosamente"
        for result in cursor.stored_results():
            resultado = result.fetchall()
            if resultado:
                mensaje = resultado[0]["respuesta"]
        
        conn.commit()
        
        exito = not ("❌" in mensaje or "Error" in mensaje)
        
        return jsonify({
            "exito": exito,
            "mensaje": mensaje
        })
        
    except Exception as e:
        logging.error(f"Error registrando persona: {e}")
        return jsonify({
            "exito": False,
            "mensaje": f"❌ Error al registrar persona: {str(e)}"
        })
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@registro_bautizos_bp.route("/bautizos_por_fecha", methods=["GET"])
def bautizos_por_fecha():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM vta_bautizos ORDER BY fechaBautizo DESC")
        bautizos = cursor.fetchall()
        
        return render_template("bautizos_por_fecha.html", bautizos=bautizos)

    except Exception as e:
        logging.error(f"Error consultando bautizos: {e}")
        return render_template("bautizos_por_fecha.html", bautizos=[], error="Error al cargar los datos")
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


