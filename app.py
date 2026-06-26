from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import psycopg

from config import *



app = Flask(__name__)

app.secret_key = "super_clave_secreta_123"

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def conectar():

    return psycopg.connect(

        host=DB_HOST,

        port=DB_PORT,

        dbname=DB_NAME,

        user=DB_USER,

        password=DB_PASSWORD

    )



@app.route("/")
def home():

    liberar_reservas()

    # Conexión a PostgreSQL
    conn = conectar()
    cursor = conn.cursor()

    # Obtener configuración
    cursor.execute("""
    SELECT *
    FROM configuracion
    WHERE id = 1
""")
    config = cursor.fetchone()

    print(config)

    # Obtener números
    cursor.execute("""
        SELECT numero, estado
        FROM numeros
        ORDER BY numero
    """)

    datos = cursor.fetchall()

    numeros = []

    for n in datos:

        numeros.append({
            "numero": n[0],
            "estado": n[1]
        })

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        numeros=numeros,
        config=config
    )



@app.route("/compra")
def compra():

    numeros_raw = request.args.get("numeros")

    print("RAW:", numeros_raw)
    print("TIPO:", type(numeros_raw))

    numeros = numeros_raw.split(",")

    print("LISTA:", numeros)

    return render_template(
        "compra.html",
        numeros=numeros
    )

@app.route("/reservar", methods=["POST"])
def reservar():



    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    ciudad = request.form["ciudad"]

    correo = request.form.get("correo")

    metodo_pago = request.form["metodo_pago"]

    numeros = request.form.getlist("numeros")

    conn = conectar()

    cursor = conn.cursor()

    # Crear compra

    cursor.execute("""

        INSERT INTO compras (

            nombre,
            telefono,
            correo,
            ciudad,
            metodo_pago

        )

        VALUES (%s,%s,%s,%s,%s)

        RETURNING id

    """,

    (

        nombre,
        telefono,
        correo,
        ciudad,
        metodo_pago

    ))

    compra_id = cursor.fetchone()[0]

    # Hora límite

    limite = datetime.now() + timedelta(minutes=30)

    # Reservar números

    for numero in numeros:

        cursor.execute("""

            UPDATE numeros

            SET

                estado='reservado',

                compra_id=%s,

                reservado_hasta=%s

            WHERE numero=%s

        """,

        (

            compra_id,
            limite,
            numero

        ))

    conn.commit()

    cursor.close()

    conn.close()

    total = len(numeros) * 20000

    

    return render_template(
    "pago.html",
    numeros=numeros,
    total=total,
    compra_id=compra_id
)

@app.route("/subir_comprobante", methods=["POST"])
def subir_comprobante():

    compra_id = request.form["compra_id"]

    archivo = request.files["comprobante"]

    if archivo.filename == "":
        return "No seleccionaste ningún archivo"

    nombre_archivo = secure_filename(archivo.filename)

    ruta = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nombre_archivo
    )

    archivo.save(ruta)

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE compras

        SET comprobante = %s

        WHERE id = %s

    """,

    (nombre_archivo, compra_id))

    conn.commit()

    cursor.close()
    conn.close()

    return """
    <h1>Comprobante enviado correctamente</h1>

    <a href='/'>
        Volver al inicio
    </a>
    """

@app.route("/admin")
def admin():

    return render_template(
        "admin/login.html"
    )


@app.route(
    "/admin/login",
    methods=["POST"]
)
def login_admin():

    usuario = request.form["usuario"]
    password = request.form["password"]

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT id

        FROM admin

        WHERE usuario=%s
        AND password=%s

    """,

    (usuario,password))

    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin:

        session["admin"] = admin[0]

        return redirect(
            "/admin/dashboard"
        )

    return "Credenciales incorrectas"

@app.route("/admin/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/admin")

    liberar_reservas()

    conn = conectar()
    cursor = conn.cursor()

    # Compras pendientes
    cursor.execute("""
        SELECT
            id,
            nombre,
            telefono,
            metodo_pago,
            comprobante
        FROM compras
        WHERE estado='pendiente'
        ORDER BY id DESC
    """)

    compras = cursor.fetchall()

    # Vendidos
    cursor.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE estado='vendido'
    """)

    vendidos = cursor.fetchone()[0]

    # Reservados
    cursor.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE estado='reservado'
    """)

    reservados = cursor.fetchone()[0]

    # Disponibles
    cursor.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE estado='disponible'
    """)

    disponibles = cursor.fetchone()[0]

    # Dinero recaudado
    precio_boleta = 20000
    recaudado = vendidos * precio_boleta

    cursor.close()
    conn.close()

    return render_template(
    "admin/dashboard.html",
    compras=compras,
    vendidos=vendidos,
    reservados=reservados,
    disponibles=disponibles,
    recaudado=recaudado
)


@app.route("/admin/aprobar/<int:id>")
def aprobar(id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE compras

        SET estado='aprobado'

        WHERE id=%s

    """,

    (id,))

    cursor.execute("""

        UPDATE numeros

        SET estado='vendido'

        WHERE compra_id=%s

    """,

    (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        "/admin/dashboard"
    )


@app.route("/admin/rechazar/<int:id>")
def rechazar(id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE numeros

        SET

            estado='disponible',

            compra_id=NULL,

            reservado_hasta=NULL

        WHERE compra_id=%s

    """,

    (id,))

    cursor.execute("""

        DELETE FROM compras

        WHERE id=%s

    """,

    (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        "/admin/dashboard"
    )

@app.route("/uploads/<filename>")
def uploads(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


def liberar_reservas():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE numeros

        SET
            estado = 'disponible',
            compra_id = NULL,
            reservado_hasta = NULL

        WHERE
            estado = 'reservado'
            AND reservado_hasta < NOW()

    """)

    conn.commit()

    cursor.close()
    conn.close()

def liberar_reservas():

    conn = conectar()

    cursor = conn.cursor()

    # Obtener compras vencidas
    cursor.execute("""

        SELECT DISTINCT compra_id

        FROM numeros

        WHERE
            estado = 'reservado'
            AND reservado_hasta < NOW()
            AND compra_id IS NOT NULL

    """)

    compras_vencidas = cursor.fetchall()

    # Liberar números
    cursor.execute("""

        UPDATE numeros

        SET
            estado = 'disponible',
            compra_id = NULL,
            reservado_hasta = NULL

        WHERE
            estado = 'reservado'
            AND reservado_hasta < NOW()

    """)

    # Eliminar compras pendientes vencidas
    for compra in compras_vencidas:

        cursor.execute("""

            DELETE FROM compras

            WHERE id = %s
            AND estado = 'pendiente'

        """, (compra[0],))

    conn.commit()

    cursor.close()
    conn.close()


@app.route("/admin/configuracion", methods=["GET", "POST"])
def configuracion():

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        nombre = request.form["nombre_rifa"]
        precio = request.form["precio_numero"]
        fecha = request.form["fecha_sorteo"]
        nequi = request.form["nequi"]
        bancolombia = request.form["bancolombia"]
        daviplata = request.form["daviplata"]
        imagen = request.form["imagen_premio"]

        cursor.execute("""
            UPDATE configuracion
            SET
                nombre_rifa=%s,
                precio_numero=%s,
                fecha_sorteo=%s,
                nequi=%s,
                bancolombia=%s,
                daviplata=%s,
                imagen_premio=%s
            WHERE id=1
        """, (
            nombre,
            precio,
            fecha,
            nequi,
            bancolombia,
            daviplata,
            imagen
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM configuracion
        WHERE id=1
    """)

    config = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "admin/configuracion.html",
        config=config
    )



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)