from flask import Flask, request, redirect, send_from_directory, session, render_template_string, jsonify
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
        port=int(os.getenv("DB_PORT", 3306)),
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

        cursor.execute(
            "SELECT idioma FROM ajustes WHERE usuario_id = %s",
            (usuario_id,)
        )
        configuracion = cursor.fetchone()
        idioma = configuracion[0] if configuracion else "Español"

        with open(os.path.join(app.root_path, "home.html"), "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        return render_template_string(
            contenido,
            NOMBRE_USUARIO=usuario[0],
            idioma=idioma
        )

    except mysql.connector.Error as error:
        print("Error al cargar Home:", error)
        return "No se pudo cargar el inicio."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/ajustes.html")
def ajustes():
    if "usuario_id" not in session:
        return redirect("/iniciar-sesion.html")

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT notificaciones, modo_oscuro, idioma FROM ajustes WHERE usuario_id = %s",
        (session["usuario_id"],)
    )

    configuracion = cursor.fetchone()

    if configuracion is None:
        cursor.execute(
            """
            INSERT INTO ajustes (usuario_id)
            VALUES (%s)
            """,
            (session["usuario_id"],)
        )
        conexion.commit()

        configuracion = (1, 0, "Español")

    cursor.close()
    conexion.close()

    with open("ajustes.html", "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

    return render_template_string(
        contenido,
        notificaciones=configuracion[0],
        modo_oscuro=configuracion[1],
        idioma=configuracion[2]
    )


@app.route("/guardar-ajustes", methods=["POST"])
def guardar_ajustes():
    if "usuario_id" not in session:
        return redirect("/iniciar-sesion.html")

    notificaciones = 1 if request.form.get("notificaciones") == "on" else 0
    modo_oscuro = 1 if request.form.get("modo_oscuro") == "on" else 0
    idioma = request.form.get("idioma")

    if idioma not in ["Español", "Inglés", "Portugués"]:
        idioma = "Español"

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE ajustes
        SET notificaciones = %s,
            modo_oscuro = %s,
            idioma = %s
        WHERE usuario_id = %s
        """,
        (notificaciones, modo_oscuro, idioma, session["usuario_id"])
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect("/ajustes.html")


@app.route("/postularse.html")
def postularse():
    if "usuario_id" not in session:
        return redirect("/iniciar-sesion.html")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id, puesto, empresa
            FROM postulaciones
            WHERE usuario_id = %s
            """,
            (session["usuario_id"],)
        )

        resultados = cursor.fetchall()

        # Mantener las parejas puesto/empresa que utiliza
        # actualmente postularse.html.
        postulaciones = [
            (fila[1], fila[2]) for fila in resultados
        ]

        # Guardar también el ID de cada postulación
        # para poder cancelarla desde la pantalla.
        ids_postulaciones = {
            (fila[1], fila[2]): fila[0] for fila in resultados
        }

        with open(
            os.path.join(app.root_path, "postularse.html"),
            "r",
            encoding="utf-8"
        ) as archivo:
            contenido = archivo.read()

        return render_template_string(
            contenido,
            postulaciones=postulaciones,
            ids_postulaciones=ids_postulaciones
        )

    except mysql.connector.Error as error:
        print("Error al cargar postulaciones:", error)
        return "No se pudieron cargar las postulaciones."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/postularse", methods=["POST"])
def guardar_postulacion():
    if "usuario_id" not in session:
        return redirect("/iniciar-sesion.html")

    puesto = request.form.get("puesto")
    empresa = request.form.get("empresa")

    ofertas = {
        "Desarrollador Web": "TechSolutions",
        "Analista de Marketing": "Nova Marketing",
        "Atención al Cliente": "Grupo Conecta",
        "Contador/a": "Estudio Álvarez"
    }

    if puesto not in ofertas or ofertas[puesto] != empresa:
        return redirect("/postularse.html")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id FROM postulaciones
            WHERE usuario_id = %s AND puesto = %s AND empresa = %s
            """,
            (session["usuario_id"], puesto, empresa)
        )

        existente = cursor.fetchone()

        if not existente:
            cursor.execute(
                """
                INSERT INTO postulaciones (usuario_id, puesto, empresa)
                VALUES (%s, %s, %s)
                """,
                (session["usuario_id"], puesto, empresa)
            )
            conexion.commit()

        return redirect("/postularse.html")

    except mysql.connector.Error as error:
        print("Error al guardar postulación:", error)
        return "No se pudo guardar la postulación."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


# NUEVA FUNCIONALIDAD: CANCELAR POSTULACIÓN
@app.route("/cancelar-postulacion/<int:postulacion_id>", methods=["POST"])
def cancelar_postulacion(postulacion_id):

    if "usuario_id" not in session:
        return redirect("/iniciar-sesion")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM postulaciones
            WHERE id = %s AND usuario_id = %s
            """,
            (postulacion_id, session["usuario_id"])
        )

        conexion.commit()

        return redirect("/postularse.html")

    except mysql.connector.Error as error:
        print("Error al cancelar postulación:", error)
        return "No se pudo cancelar la postulación."

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
    except (ValueError, TypeError):
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


@app.route("/perfil.html")
def perfil():
    if "usuario_id" not in session:
        return redirect("/iniciar-sesion.html")

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT nombre, apellido, email FROM usuarios WHERE id = %s",
            (session["usuario_id"],)
        )
        usuario = cursor.fetchone()

        if not usuario:
            session.clear()
            return redirect("/iniciar-sesion.html")

        with open("perfil.html", "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        return render_template_string(
            contenido,
            nombre=usuario[0],
            apellido=usuario[1],
            email=usuario[2]
        )

    except mysql.connector.Error as error:
        print("Error al cargar perfil:", error)
        return "No se pudo cargar el perfil."

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/cerrar-sesion")
def cerrar_sesion():
    session.clear()
    return redirect("/iniciar-sesion")


@app.route("/perfil-laboral")
@app.route("/perfil-laboral/perfillaboral.html")
def perfil_laboral():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect("/iniciar-sesion")

    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM perfil_laboral WHERE usuario_id = %s", (usuario_id,))
        perfil = cursor.fetchone()
        columns = [item[0] for item in cursor.description] if cursor.description else []
        datos = dict(zip(columns, perfil)) if perfil else {}

        with open(os.path.join(app.root_path, "perfil laboral", "perfillaboral.html"), "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        return render_template_string(contenido, perfil=datos)
    except mysql.connector.Error as error:
        print("Error al cargar el perfil:", error)
        return "No se pudo cargar el perfil laboral.", 500
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/perfil-laboral/completar")
@app.route("/perfil-laboral/completar perfil.html")
def completar_perfil():
    if not session.get("usuario_id"):
        return redirect("/iniciar-sesion")

    with open(os.path.join(app.root_path, "perfil laboral", "completar perfil.html"), "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    return render_template_string(contenido)


@app.route("/guardar-perfil", methods=["POST"])
def guardar_perfil():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "Debes iniciar sesión."}), 401

    datos = request.get_json(silent=True) or {}
    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute("SELECT id FROM perfil_laboral WHERE usuario_id = %s", (usuario_id,))
        existente = cursor.fetchone()

        valores = (
            datos.get("telefono") or None,
            datos.get("ciudad") or None,
            datos.get("nivelEstudios") or None,
            datos.get("habilidadesTexto") or None,
            datos.get("experienciaTexto") or None,
            datos.get("cursosTexto") or None,
            datos.get("edad") or None,
            datos.get("contacto") or None,
        )

        if existente:
            cursor.execute("""
                UPDATE perfil_laboral
                SET telefono=%s, ciudad=%s, nivel_estudios=%s, habilidades=%s,
                    experiencia=%s, estudios=%s, edad=%s, medio_contacto=%s
                WHERE usuario_id=%s
            """, valores + (usuario_id,))
        else:
            cursor.execute("""
                INSERT INTO perfil_laboral
                (usuario_id, telefono, ciudad, nivel_estudios, habilidades,
                 experiencia, estudios, edad, medio_contacto)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (usuario_id,) + valores)

        conexion.commit()
        return jsonify({"mensaje": "Perfil guardado correctamente"})
    except mysql.connector.Error as error:
        if conexion:
            conexion.rollback()
        print("Error al guardar perfil:", error)
        return jsonify({"error": "No se pudo guardar el perfil."}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@app.route("/perfil-estatico/<path:archivo>")
def archivos_perfil(archivo):
    return send_from_directory(os.path.join(app.root_path, "perfil laboral"), archivo)


if __name__ == "__main__":
    app.run(debug=True)
