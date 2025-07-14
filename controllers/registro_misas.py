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
registromisas_bp = Blueprint('registromisas_bp', __name__)

load_dotenv()
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
BUCKET_NAME = os.getenv("AWS_BUCKET")
try:
    s3.list_buckets()
    print("✅ Conexión con S3 exitosa.")
except Exception as e:
    print("❌ Error de conexión con S3:", str(e))

@registromisas_bp.route("/docseventos", methods=["GET", "POST"])
def index():
    mensaje = session.pop("mensaje", "")  # Mostrar mensaje solo una vez
    documentos = []

    if request.method == "POST":
        archivo = request.files.get("archivo")
        if archivo and archivo.filename.endswith(".pdf"):
            nombre_s3 = f"pdfs/{archivo.filename}"
            try:
                s3.upload_fileobj(archivo, BUCKET_NAME, nombre_s3, ExtraArgs={
                    'ContentType': 'application/pdf',
                    'ContentDisposition': 'inline'
                })
                session["mensaje"] = "✅ Archivo subido correctamente."
            except Exception as e:
                session["mensaje"] = f"❌ Error al subir el archivo: {str(e)}"
        return redirect(url_for("registromisas_bp.index"))

    # Obtener lista de archivos PDF (solo en GET)
    try:
        respuesta = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="pdfs/")
        for obj in respuesta.get("Contents", []):
            key = obj["Key"]
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': key, 'ResponseContentDisposition': 'inline'},
                ExpiresIn=3600
            )
            documentos.append(url)
    except Exception as e:
        mensaje += f" | Error al listar archivos: {str(e)}"

    return render_template("registrardocs.html", documentos=documentos, mensaje=mensaje)



@registromisas_bp.route("/registrar_misas", methods=["GET", "POST"])
def registrar_misas():
    
    mensaje = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vta_iglesias")
        iglesias = cursor.fetchall()
        cursor.execute("select * from tipomisas order by tipomisas desc")
        tipomisas = cursor.fetchall()
        cursor.execute("select * from intencionesmisas")
        intenciones = cursor.fetchall()
        #print(iglesias)
    finally:
        cursor.close()
        conn.close()

    if request.method == "POST":
        try:
            fecha_misa = request.form["fecha_misa"]
            hora_misa = request.form["hora_misa"]
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"HORA MISA: {hora_misa}")
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
            
            # Imprimir los datos
            print(f"Fecha de la misa: {fecha_misa}")
            print(f"Hora de la misa: {hora_misa}")
            print(f"Ofrece: {ofrece}")
            print(f"Detalle: {detalle}")
            print(f"ID de la iglesia: {id_iglesia}")
            print(f"ID del tipo de misa: {id_tipo_misa}")
            print(f"ID de la intención de misa: {id_intencion}")

            if registrar_recibo:
                print("Datos del recibo:")
                print(f"Número de recibo: {nro_recibo}")
                print(f"Contribuyente: {contribuyente}")
                print(f"Monto: {monto}")

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

    return render_template("registromisas.html", mensaje=mensaje, iglesias=iglesias, tipomisas=tipomisas,intenciones=intenciones)



@registromisas_bp.route("/registrar_recibo/<int:idmisas>", methods=["POST"])
def registrar_recibo(idmisas):
    nrorecibo = request.form["nrorecibo"]
    contribuyente = request.form["contribuyente"]
    monto = request.form["monto"]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("registrar_recibo_misa", [
            1,
            idmisas,
            nrorecibo,
            contribuyente,
            monto
            
        ])
        conn.commit()
    except Exception as e:
        print("Error registrando recibo:", e)
        # puedes guardar un mensaje en flash o log
    finally:
        cursor.close()
        conn.close()

    return redirect("/misas_por_fecha")

from datetime import datetime, timedelta

@registromisas_bp.route("/misas_por_fecha", methods=["GET"])
def misas_por_fecha():
    fecha_str = request.args.get("fecha")
    
    # Si no hay fecha, usar hoy
    if fecha_str:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    else:
        fecha = datetime.today().date()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vta_misas WHERE fecha = %s", (fecha,))
    misas = cursor.fetchall()
    cursor.close()
    conn.close()

    # Calcular fechas anterior y siguiente
    anterior = fecha - timedelta(days=1)
    siguiente = fecha + timedelta(days=1)

    return render_template("misas_por_fecha.html", 
                           misas=misas, 
                           fecha=fecha, 
                           anterior=anterior, 
                           siguiente=siguiente)