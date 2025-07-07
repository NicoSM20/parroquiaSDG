from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from config.db import get_connection
from services.plantnet_service import identificar_por_nombre
from services.wikipedia_service import get_wikipedia_plant_image,get_wikipedia_plant_images
from datetime import datetime,timedelta
import logging

import os
import boto3
from flask import Flask, render_template, request
from dotenv import load_dotenv


registromatrimonios_bp = Blueprint('registromatrimonios_bp', __name__)


@registromatrimonios_bp.route("/registrar_matrimonios", methods=["GET", "POST"])
def registro_matrimonios():
    
    mensaje = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vta_iglesias")
        iglesias = cursor.fetchall()
        cursor.execute("select * from aniosparroquial")
        añosparr = cursor.fetchall()
        cursor.execute("select * from vta_sacerdotes;")
        sacerdotes = cursor.fetchall()
        cursor.execute("select * from estadosciviles;")
        estadosciviles = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if request.method == "POST":
        try:
            fecha_misa = request.form["fecha_misa"]
            hora_misa = request.form["hora_misa"]
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"HORA MISA: {hora_misa}")
            print("HORA MISA: ",hora_misa)
            ofrece = request.form["ofrece"]
            detalle = request.form["detalle"]
            id_iglesia = int(request.form["idiglesias"])
            id_tipo_misa = int(request.form["idtipomisas"])
            id_intencion = int(request.form["idintencionesmisa"])

            # Recibo (solo si checkbox fue marcado)
            registrar_recibo = "registrarRecibo" in request.form  # True/False
            nro_recibo = request.form["nrorecibo"] if registrar_recibo else None
            contribuyente = request.form["contribuyente"] if registrar_recibo else None
            monto = request.form["monto"] if registrar_recibo else None
            monto = float(monto) if monto else 0.0

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.callproc("gestionar_misa", [
                1,              # ev = 1 (insertar)
                None,           # i_idMisa = NULL
                fecha_misa,
                hora_misa,
                ofrece,
                detalle,
                id_iglesia,
                id_tipo_misa,
                id_intencion,
                registrar_recibo,
                nro_recibo,
                contribuyente,
                monto
            ])

            for result in cursor.stored_results():
                mensaje = result.fetchall()[0]["respuesta"]
            #print(mensaje)
            conn.commit()
            
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"mensaje": mensaje})
            #print(mensaje)
            #render_template("registromisas.html", mensaje=mensaje, iglesias=iglesias, tipomisas=tipomisas,intenciones=intenciones)
        except Exception as e:
            mensaje = f"❌ Error en el servidor: {str(e)}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return render_template("registromatrimonios.html", 
                           mensaje=mensaje, 
                           iglesias=iglesias, 
                           añosparr=añosparr,
                           sacerdotes=sacerdotes, 
                           estadosciviles=estadosciviles)
@registromatrimonios_bp.route("/buscar_persona_por_dni", methods=["POST"])
def buscar_persona_por_dni():
    dni = request.json.get("dni")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.callproc("buscar_persona", [dni])

        for result in cursor.stored_results():
            persona = result.fetchone()
            if persona:
                print(persona)
                return jsonify({
                    "existe": True,
                    "id": persona["idpersonas"],
                    "nombre": persona["nombre"]
                })
            else:
                return jsonify({"existe": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@registromatrimonios_bp.route("/registrar_persona", methods=["POST"])
def registrar_persona():
    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Llamar al procedimiento almacenado
        cursor.callproc("registrar_persona", (
            data["dni"],
            data["nombres"],
            data["apellido1"],
            data["apellido2"],
            data["genero"]
        ))

        # Obtener el mensaje de salida del SELECT dentro del procedimiento
        for result in cursor.stored_results():
            mensaje = result.fetchall()[0]["respuesta"]

        conn.commit()
        return jsonify({"mensaje": mensaje})
    except Exception as e:
        return jsonify({"error": f"❌ Error en servidor: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

