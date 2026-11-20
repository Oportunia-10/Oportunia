# Oportunia

Oportunia es una plataforma web orientada a facilitar el acceso a oportunidades de formación y empleo.

## Tecnologías utilizadas

- Python
- Flask
- MySQL
- HTML5
- CSS3
- Bootstrap

## Funcionalidades

- Registro de usuarios.
- Inicio de sesión.
- Conexión con base de datos MySQL.
- Configuración de preferencias del usuario.
- Gestión de capacitaciones y progreso.
- Postulaciones a oportunidades.

**Nota:** La sección Perfil Laboral se encuentra en proceso de integración.

## Requisitos

- Python 3 instalado.
- MySQL Server.
- MySQL Workbench (recomendado).

## Instalación

1. Clonar el repositorio:

   git clone https://github.com/Oportunia-10/Oportunia.git

2. Entrar en la carpeta:

   cd Oportunia

3. Crear un entorno virtual:

   python -m venv venv

4. Activar el entorno virtual en Windows:

   .\venv\Scripts\Activate.ps1

5. Instalar las dependencias:

   pip install -r requirements.txt

## Configuración de la base de datos

1. Abrir MySQL Workbench.
2. Crear una base de datos llamada oportunia.
3. Importar el archivo database.sql.
4. Crear un archivo .env en la carpeta principal con las variables DB_HOST, DB_USER, DB_PASSWORD, DB_NAME y FLASK_SECRET_KEY.

## Ejecutar el proyecto

Con el entorno virtual activado y MySQL funcionando:

   python app.py

Abrir en el navegador:

http://127.0.0.1:5000

## Repositorio

https://github.com/Oportunia-10/Oportunia

## Estado del proyecto

Proyecto académico en desarrollo.
