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
2. Abrir e ejecutar el archivo `database.sql` completo.
3. Copiar `.env.example` como `.env` y configurar las credenciales de MySQL.

Ejemplo:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_clave
DB_NAME=oportunia
FLASK_SECRET_KEY=una_clave_segura
```

## Ejecutar el proyecto

Desde la carpeta principal:

```powershell
pip install -r requirements.txt
python app.py
```

Abrir: http://127.0.0.1:5000

No es necesario ejecutar el servidor dentro de `backend/`: el sistema está integrado en `app.py`.

## Repositorio

https://github.com/Oportunia-10/Oportunia

## Estado del proyecto

Proyecto académico en desarrollo.
