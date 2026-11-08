CREATE DATABASE IF NOT EXISTS ControlLecheDB;
USE ControlLecheDB;

-- 1. Tabla de Productores
CREATE TABLE IF NOT EXISTS Productores (
    ProductorID INT AUTO_INCREMENT PRIMARY KEY,
    Cedula VARCHAR(10) UNIQUE NOT NULL,
    NombreCompleto VARCHAR(100) NOT NULL,
    Telefono VARCHAR(15),
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Entregas Diarias
CREATE TABLE IF NOT EXISTS Entregas (
    EntregaID INT AUTO_INCREMENT PRIMARY KEY,
    ProductorID INT NOT NULL,
    LitrosEntregados DECIMAL(8,2) NOT NULL,
    FechaEntrega DATETIME DEFAULT CURRENT_TIMESTAMP,
    Estado VARCHAR(20) DEFAULT 'Registrada',
    FOREIGN KEY (ProductorID) REFERENCES Productores(ProductorID)
);

-- 3. Tabla de Auditoría (Situación Crítica: Trazabilidad)
CREATE TABLE IF NOT EXISTS AuditoriaEntregas (
    AuditoriaID INT AUTO_INCREMENT PRIMARY KEY,
    EntregaID INT NOT NULL,
    LitrosAnteriores DECIMAL(8,2) NOT NULL,
    LitrosNuevos DECIMAL(8,2) NOT NULL,
    MotivoCambio VARCHAR(255) NOT NULL,
    UsuarioAutoriza VARCHAR(50) NOT NULL,
    FechaModificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (EntregaID) REFERENCES Entregas(EntregaID)
);

-- Datos iniciales de prueba
INSERT INTO Productores (Cedula, NombreCompleto, Telefono) VALUES 
('0501234567', 'Juan Pérez', '0991234567'),
('0509876543', 'María López', '0987654321'),
('0503456789', 'Carlos Toapanta', '0971122334');