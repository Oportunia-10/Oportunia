
import os
from flask import Flask, render_template, request, jsonify
from conexion import conectar

CARPETA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(CARPETA_PROYECTO, "perfil laboral"),
    static_folder=os.path.join(CARPETA_PROYECTO, "perfil laboral"),
    static_url_path="/perfil-estatico"
)


@app.route("/")
def inicio():
    return "Oportunia está funcionando"


@app.route("/completar-perfil")
def completar_perfil():
    return render_template("completar perfil.html")


@app.route("/probar-conexion")
def probar_conexion():
    try:
        conexion = conectar()
        conexion.close()
        return "Conexión con MySQL exitosa"

    except Exception as error:
        return f"Error al conectar con MySQL: {error}"


@app.route("/guardar-perfil", methods=["POST"])
def guardar_perfil():

    datos = request.get_json(silent=True) or {}

    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # 1. Guardar datos personales
        sql_perfil = """
            INSERT INTO perfil
            (nombre, apellido, edad, ciudad, email, telefono, contacto_preferido)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        valores_perfil = (
            datos.get("nombre"),
            datos.get("apellido"),
            datos.get("edad"),
            datos.get("ciudad"),
            datos.get("email"),
            datos.get("telefono") or None,
            datos.get("contacto") or None
        )

        cursor.execute(sql_perfil, valores_perfil)

        # Obtener el ID del perfil creado
        perfil_id = cursor.lastrowid

        # 2. Guardar estudios
        nivel = datos.get("nivelEstudios")

        if nivel:
            sql_estudios = """
                INSERT INTO estudios
                (perfil_id, nivel_educativo)
                VALUES (%s, %s)
            """

            cursor.execute(sql_estudios, (perfil_id, nivel))

        # 3. Guardar habilidades
        habilidades = datos.get("habilidadesTexto", "")

        if habilidades:
            lista_habilidades = habilidades.replace("\n", ",").split(",")

            for habilidad in lista_habilidades:
                habilidad = habilidad.strip()

                if habilidad:
                    sql_habilidades = """
                        INSERT INTO habilidades (perfil_id, habilidad)
                        VALUES (%s, %s)
                    """

                    cursor.execute(sql_habilidades, (perfil_id, habilidad))

        # 4. Guardar cursos
        cursos = datos.get("cursosTexto", "").strip()

        if cursos:
            sql_cursos = """
                INSERT INTO cursos (perfil_id, nombre_curso)
                VALUES (%s, %s)
            """

            cursor.execute(sql_cursos, (perfil_id, cursos))

        # 5. Guardar experiencia laboral
        experiencia = datos.get("experienciaTexto", "").strip()

        if experiencia:
            sql_experiencia = """
                INSERT INTO experiencia_laboral
                (perfil_id, descripcion)
                VALUES (%s, %s)
            """

            cursor.execute(sql_experiencia, (perfil_id, experiencia))

        # Confirmar todos los cambios
        conexion.commit()

        return jsonify({
            "mensaje": "Perfil guardado correctamente",
            "perfil_id": perfil_id
        })

    except Exception as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


if __name__ == "__main__":
    app.run(debug=False, port=5001)