-- Script de instalación portable para Oportunia
-- Ejecutar completo en MySQL Workbench.
CREATE DATABASE IF NOT EXISTS oportunia
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE oportunia;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS perfil;
DROP TABLE IF EXISTS estudios;
DROP TABLE IF EXISTS habilidades;
DROP TABLE IF EXISTS cursos;
DROP TABLE IF EXISTS experiencia_laboral;
DROP TABLE IF EXISTS ajustes;
DROP TABLE IF EXISTS capacitaciones;
DROP TABLE IF EXISTS postulaciones;
DROP TABLE IF EXISTS perfil_laboral;
DROP TABLE IF EXISTS usuarios;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ajustes (
    id INT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    notificaciones TINYINT(1) DEFAULT 1,
    modo_oscuro TINYINT(1) DEFAULT 0,
    idioma VARCHAR(30) DEFAULT 'Español',
    PRIMARY KEY (id),
    UNIQUE KEY uq_ajustes_usuario (usuario_id),
    CONSTRAINT fk_ajustes_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE postulaciones (
    id INT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    puesto VARCHAR(150) NOT NULL,
    empresa VARCHAR(150) DEFAULT NULL,
    fecha_postulacion TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('enviada','en_revision','aceptada','rechazada') DEFAULT 'enviada',
    PRIMARY KEY (id),
    KEY idx_postulaciones_usuario (usuario_id),
    CONSTRAINT fk_postulaciones_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE capacitaciones (
    id INT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    nombre_capacitacion VARCHAR(150) NOT NULL,
    descripcion TEXT,
    estado ENUM('pendiente','en_curso','completada') DEFAULT 'pendiente',
    progreso TINYINT UNSIGNED DEFAULT 0,
    fecha_inicio DATE DEFAULT NULL,
    fecha_completado DATE DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuario_capacitacion (usuario_id,nombre_capacitacion),
    CONSTRAINT fk_capacitaciones_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE perfil_laboral (
    id INT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    telefono VARCHAR(30) DEFAULT NULL,
    direccion VARCHAR(150) DEFAULT NULL,
    estudios TEXT,
    experiencia TEXT,
    habilidades TEXT,
    edad INT DEFAULT NULL,
    ciudad VARCHAR(100) DEFAULT NULL,
    medio_contacto ENUM('email','telefono','ambos') DEFAULT NULL,
    nivel_estudios VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_perfil_usuario (usuario_id),
    CONSTRAINT fk_perfil_laboral_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tablas compatibles con el módulo Perfil anterior
CREATE TABLE perfil (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    edad INT,
    ciudad VARCHAR(100),
    email VARCHAR(150),
    telefono VARCHAR(30),
    contacto_preferido VARCHAR(30),
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE estudios (
    id INT NOT NULL AUTO_INCREMENT,
    perfil_id INT NOT NULL,
    nivel_educativo VARCHAR(100),
    PRIMARY KEY (id),
    CONSTRAINT fk_estudios_perfil FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE habilidades (
    id INT NOT NULL AUTO_INCREMENT,
    perfil_id INT NOT NULL,
    habilidad VARCHAR(150),
    PRIMARY KEY (id),
    CONSTRAINT fk_habilidades_perfil FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cursos (
    id INT NOT NULL AUTO_INCREMENT,
    perfil_id INT NOT NULL,
    nombre_curso VARCHAR(200),
    PRIMARY KEY (id),
    CONSTRAINT fk_cursos_perfil FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE experiencia_laboral (
    id INT NOT NULL AUTO_INCREMENT,
    perfil_id INT NOT NULL,
    descripcion TEXT,
    PRIMARY KEY (id),
    CONSTRAINT fk_experiencia_perfil FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
