from flask import Flask, request, redirect, send_from_directory, session, render_template_string
import mysql.connector
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave-local-oportunia")


def conectar_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        use_pure=True,
        connection_timeout=10
    )


try:
    conexion = conectar_db()
    print("¡Conexión con MySQL exitosa!")
    conexion.close()
except mysql.connector.Error as error:
    print("Error al conectar con MySQL:", error)


@app.route("/")
def inicio():
    return redirect("/registrarse")


@app.route("/registrarse", methods=["GET", "POST"])
def registrarse():
    if request.method == "GET":
        return send_from_directory(app.root_path, "registrarse.html")

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    correo = request.form.get("correo", "").strip()
    contrasena = request.form.get("contrasena", "")

    if not nombre or not apellido or not correo or not contrasena:
        return "Todos los campos son obligatorios."

    contrasena_hash = generate_password_hash(contrasena)
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO usuarios (nombre, apellido, email, password)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(consulta, (nombre, apellido, correo, contrasena_hash))
        conexion.commit()

        session["usuario_id"] = cursor.lastrowid
        return redirect("/home.html")

    except IntegrityError:
        return "Ese correo ya está registrado."

    except mysql.connector.Error as error:
        print("Error al registrar usuario:", error)
        return "No se pudo completar el registro."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/iniciar-sesion", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "GET":
        return send_from_directory(app.root_path, "iniciar-sesion.html")

    correo = request.form.get("correo", "").strip()
    contrasena = request.form.get("contrasena", "")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        consulta = """
            SELECT id, password
            FROM usuarios
            WHERE email = %s
        """
        cursor.execute(consulta, (correo,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario[1], contrasena):
            session["usuario_id"] = usuario[0]
            return redirect("/home.html")

        return "Correo o contraseña incorrectos. <a href='/iniciar-sesion'>Volver</a>"

    except mysql.connector.Error as error:
        print("Error al iniciar sesión:", error)
        return "No se pudo iniciar sesión."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/home.html")
def home():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/iniciar-sesion")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT nombre FROM usuarios WHERE id = %s",
            (usuario_id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            session.clear()
            return redirect("/iniciar-sesion")

        with open(os.path.join(app.root_path, "home.html"), "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        return render_template_string(
            contenido,
            NOMBRE_USUARIO=usuario[0]
        )

    except mysql.connector.Error as error:
        print("Error al cargar Home:", error)
        return "No se pudo cargar el inicio."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/<path:archivo>")
def mostrar_archivos(archivo):
    extensiones_permitidas = (
        ".html", ".css", ".js", ".png",
        ".jpg", ".jpeg", ".svg", ".webp", ".ico"
    )

    if not archivo.lower().endswith(extensiones_permitidas):
        return "Archivo no encontrado", 404

    return send_from_directory(app.root_path, archivo)


if __name__ == "__main__":
    app.run(debug=True)
