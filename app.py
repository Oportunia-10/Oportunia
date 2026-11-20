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


@app.route("/capacitaciones.html")
def capacitaciones():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/iniciar-sesion")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursos_iniciales = [
            (
                usuario_id,
                "Cómo crear tu CV",
                "Aprendé a preparar tu currículum."
            ),
            (
                usuario_id,
                "Preparación para entrevistas",
                "Aprendé a prepararte para una entrevista laboral."
            )
        ]

        consulta_insertar = """
            INSERT IGNORE INTO capacitaciones
            (usuario_id, nombre_capacitacion, descripcion)
            VALUES (%s, %s, %s)
        """

        cursor.executemany(consulta_insertar, cursos_iniciales)
        conexion.commit()

        consulta = """
            SELECT id, nombre_capacitacion, descripcion,
                   estado, progreso
            FROM capacitaciones
            WHERE usuario_id = %s
            ORDER BY id
        """

        cursor.execute(consulta, (usuario_id,))
        cursos = cursor.fetchall()

        with open(
            os.path.join(app.root_path, "capacitaciones.html"),
            "r",
            encoding="utf-8"
        ) as archivo:
            contenido = archivo.read()

        return render_template_string(
            contenido,
            cursos=cursos
        )

    except mysql.connector.Error as error:
        print("Error al cargar capacitaciones:", error)
        return "No se pudieron cargar las capacitaciones."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.route("/capacitaciones/<int:curso_id>/comenzar", methods=["POST"])
def comenzar_capacitacion(curso_id):
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/iniciar-sesion")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        consulta = """
            UPDATE capacitaciones
            SET estado = 'en_curso',
                fecha_inicio = COALESCE(fecha_inicio, CURDATE())
            WHERE id = %s
              AND usuario_id = %s
              AND estado = 'pendiente'
        """

        cursor.execute(consulta, (curso_id, usuario_id))
        conexion.commit()

        return redirect("/capacitaciones.html")

    except mysql.connector.Error as error:
        print("Error al comenzar capacitación:", error)
        return "No se pudo comenzar la capacitación."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.route("/capacitaciones/<int:curso_id>/progreso", methods=["POST"])
def actualizar_progreso(curso_id):
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/iniciar-sesion")

    try:
        progreso = int(request.form.get("progreso", -1))
    except ValueError:
        return "El progreso debe ser un número."

    if progreso < 0 or progreso > 100:
        return "El progreso debe estar entre 0 y 100."

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        consulta = """
            UPDATE capacitaciones
            SET progreso = %s,
                estado = CASE
                    WHEN %s = 100 THEN 'completada'
                    WHEN %s > 0 THEN 'en_curso'
                    ELSE 'pendiente'
                END,
                fecha_inicio = CASE
                    WHEN %s > 0 THEN COALESCE(fecha_inicio, CURDATE())
                    ELSE fecha_inicio
                END,
                fecha_completado = CASE
                    WHEN %s = 100 THEN CURDATE()
                    ELSE NULL
                END
            WHERE id = %s AND usuario_id = %s
        """

        cursor.execute(
            consulta,
            (
                progreso,
                progreso,
                progreso,
                progreso,
                progreso,
                curso_id,
                usuario_id
            )
        )

        conexion.commit()

        return redirect("/capacitaciones.html")

    except mysql.connector.Error as error:
        print("Error al actualizar progreso:", error)
        return "No se pudo actualizar el progreso."

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
