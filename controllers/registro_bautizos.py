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


registrobautizos_bp = Blueprint('registrobautizos_bp', __name__)


@registrobautizos_bp.route("/registrar_bautizos", methods=["GET", "POST"])
def registro_bautizos():
    
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

    return render_template("registrobautizos.html", mensaje=mensaje, iglesias=iglesias, añosparr=añosparr,sacerdotes=sacerdotes)
