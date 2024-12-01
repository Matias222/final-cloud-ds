-- Drop the database if it already exists
DROP DATABASE IF EXISTS gestion_vuelos;

-- Create the database
CREATE DATABASE gestion_vuelos;

-- Use the created database
USE gestion_vuelos;

-- Set the global timezone to Peru time (UTC-5)
SET GLOBAL time_zone = '-05:00';

-- Ensure the session timezone is also set to Peru time (UTC-5)
SET time_zone = '-05:00';

-- Create the Usuarios table
CREATE TABLE Usuarios (
    user_id VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- Create the Aerolineas table
CREATE TABLE Aerolineas (
    tenant_id VARCHAR(255) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    pais_origen VARCHAR(100) NOT NULL
);

-- Create the Vuelos table
CREATE TABLE Vuelos (
    tenant_id VARCHAR(255),
    codigo VARCHAR(50) NOT NULL,
    id_vuelo VARCHAR(255) PRIMARY KEY,
    origen VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    fecha_salida DATETIME NOT NULL,
    fecha_llegada DATETIME NOT NULL,
    capacidad INT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES Aerolineas(tenant_id) ON DELETE CASCADE
);

-- Create the Compras table
CREATE TABLE Compras (
    user_id VARCHAR(255),
    id_vuelo VARCHAR(255),
    fecha_compra DATETIME NOT NULL,
    cantidad_boletos INT NOT NULL,
    precio_total INT NOT NULL,
    PRIMARY KEY (user_id, id_vuelo),
    FOREIGN KEY (user_id) REFERENCES Usuarios(user_id) ON DELETE CASCADE,
    FOREIGN KEY (id_vuelo) REFERENCES Vuelos(id_vuelo) ON DELETE CASCADE
);

-- Create the Resena table
CREATE TABLE Resena (
    user_id VARCHAR(255),
    id_resenia VARCHAR(255) PRIMARY KEY,
    id_vuelo VARCHAR(255),
    calificacion INT NOT NULL,
    comentario TEXT,
    fecha_resena DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Usuarios(user_id) ON DELETE CASCADE,
    FOREIGN KEY (id_vuelo) REFERENCES Vuelos(id_vuelo) ON DELETE CASCADE
);

-- Create the Destinos table
CREATE TABLE Destinos (
    id_destino VARCHAR(255) PRIMARY KEY,
    ciudad VARCHAR(100) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    descripcion TEXT,
    popularidad INT NOT NULL
);
