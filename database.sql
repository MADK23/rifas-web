CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE rifas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255),
    descripcion TEXT,
    premio VARCHAR(255),
    imagen VARCHAR(255),
    precio NUMERIC(10,2),
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE compras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    ciudad VARCHAR(100),
    metodo_pago VARCHAR(50),
    comprobante VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE numeros (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(3) UNIQUE,
    compra_id INTEGER,
    estado VARCHAR(20) DEFAULT 'disponible',
    reservado_hasta TIMESTAMP,
    FOREIGN KEY(compra_id) REFERENCES compras(id) ON DELETE SET NULL
);

CREATE TABLE configuracion (
    id SERIAL PRIMARY KEY,
    nombre_rifa VARCHAR(255),
    precio_numero NUMERIC(10,2),
    fecha_sorteo DATE,
    nequi VARCHAR(100),
    bancolombia VARCHAR(100),
    daviplata VARCHAR(100),
    imagen_premio VARCHAR(255)
);

-- Insertar números del 1 al 500
INSERT INTO numeros(numero)
SELECT LPAD(generate_series(1,500)::TEXT,3,'0');

-- Insertar configuración inicial
INSERT INTO configuracion(nombre_rifa, precio_numero, fecha_sorteo)
VALUES ('Mi Rifa', 20000, CURRENT_DATE + INTERVAL '30 days');