import boto3
import random
import json
import uuid
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AMAZON_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')


# Conexión con DynamoDB
dynamodb = boto3.resource('dynamodb',aws_access_key_id=AMAZON_ACCESS_KEY_ID,aws_secret_access_key=AMAZON_SECRET_ACCESS_KEY,region_name="us-east-2")

usuarios_table = dynamodb.Table('t_usuarios')
aerolineas_table = dynamodb.Table('t_aerolineas')
vuelos_table = dynamodb.Table('t_vuelo')
destinos_table = dynamodb.Table('t_destinos')
compras_table = dynamodb.Table('t_compras')
resenias_table = dynamodb.Table('t_resenias')

# Generar usuarios
def generar_usuario():
    user_id = f"user-{random.randint(1, 100000)}"
    password = f"password{random.randint(1, 100000)}"
    return {
        'user_id': user_id,
        'password': password
    }

# Generar aerolíneas
def generar_aerolinea(index):
    return {
        'id_aerolinea': f"AER-{index:03}",
        'nombre': f"Aerolinea {index}",
        'codigo': f"{random.choice(['AA', 'UA', 'DL', 'BA', 'AF'])}{random.randint(100, 999)}",
        'pais_origen': random.choice(['USA', 'Perú', 'México', 'Canadá', 'España', 'Brasil'])
    }

# Generar vuelos
def generar_vuelo(index, aerolineas):
    aerolinea = random.choice(aerolineas)
    return {
        'id_vuelo': f"FL-{index:04}",
        'id_aerolinea': aerolinea['id_aerolinea'],
        'codigo_vuelo': f"{random.choice(['AA', 'UA', 'DL', 'BA', 'AF'])}{random.randint(1000, 9999)}",
        'origen': random.choice(['LAX', 'JFK', 'LIM', 'CDMX', 'BCN', 'GRU']),
        'destino': random.choice(['LAX', 'JFK', 'LIM', 'CDMX', 'BCN', 'GRU']),
        'fecha_salida': (datetime.now() + timedelta(days=random.randint(1, 365))).isoformat(),
        'fecha_llegada': (datetime.now() + timedelta(days=random.randint(1, 365), hours=random.randint(2, 12))).isoformat(),
        'capacidad': random.randint(100, 300)
    }

# Generar destinos
def generar_destino(index):
    return {
        'id_destino': f"DST-{index:03}",
        'ciudad': random.choice(['Lima', 'New York', 'Madrid', 'Sao Paulo', 'Paris', 'Tokyo']),
        'pais': random.choice(['Perú', 'USA', 'España', 'Brasil', 'Francia', 'Japón']),
        'descripcion': 'Un destino turístico muy popular.',
        'popularidad': random.randint(1, 10)
    }

# Generar compras
def generar_compra(user_id, vuelos):
    vuelo = random.choice(vuelos)
    return {
        'user_id': user_id,
        'id_compra': f"COM-{uuid.uuid4()}",
        'id_vuelo': vuelo['id_vuelo'],
        'fecha_compra': datetime.now().isoformat(),
        'cantidad_boletos': random.randint(1, 5),
        'precio_total': random.randint(100, 1000),
        'estado': 'pendiente'
    }

# Generar reseñas
def generar_resenia(user_id, vuelos):
    vuelo = random.choice(vuelos)
    return {
        'id_resenia': f"RES-{uuid.uuid4()}",
        'user_id': user_id,
        'id_vuelo': vuelo['id_vuelo'],
        'calificacion': random.randint(1, 5),
        'comentario': 'Muy buen vuelo!',
        'fecha_resena': datetime.now().isoformat()
    }

# Insertar usuarios
def insertar_usuarios(num_usuarios):
    for _ in range(num_usuarios):
        usuario = generar_usuario()
        usuarios_table.put_item(Item=usuario)

# Insertar aerolíneas
def insertar_aerolineas(num_aerolineas):
    aerolineas = []
    for i in range(1, num_aerolineas + 1):
        aerolinea = generar_aerolinea(i)
        aerolineas_table.put_item(Item=aerolinea)
        aerolineas.append(aerolinea)
    return aerolineas

# Insertar vuelos
def insertar_vuelos(num_vuelos, aerolineas):
    vuelos = []
    for i in range(1, num_vuelos + 1):
        vuelo = generar_vuelo(i, aerolineas)
        vuelos_table.put_item(Item=vuelo)
        vuelos.append(vuelo)
    return vuelos

# Insertar destinos
def insertar_destinos(num_destinos):
    for i in range(1, num_destinos + 1):
        destino = generar_destino(i)
        destinos_table.put_item(Item=destino)

# Insertar compras
def insertar_compras(num_compras, usuarios, vuelos):
    for _ in range(num_compras):
        usuario = random.choice(usuarios)
        compra = generar_compra(usuario['user_id'], vuelos)
        compras_table.put_item(Item=compra)

# Insertar reseñas
def insertar_resenias(num_resenias, usuarios, vuelos):
    for _ in range(num_resenias):
        usuario = random.choice(usuarios)
        resenia = generar_resenia(usuario['user_id'], vuelos)
        resenias_table.put_item(Item=resenia)

def cargar_datos():
    # Cargar 5000 usuarios, 50 aerolíneas, 4000 vuelos, 500 destinos, 3000 compras y 2000 reseñas
    print("Cargando usuarios...")
    insertar_usuarios(5000)

    print("Cargando aerolíneas...")
    aerolineas = insertar_aerolineas(50)

    print("Cargando vuelos...")
    vuelos = insertar_vuelos(4000, aerolineas)

    print("Cargando destinos...")
    insertar_destinos(500)

    print("Cargando compras...")
    insertar_compras(3000, [user['user_id'] for user in range(5000)], vuelos)

    print("Cargando reseñas...")
    insertar_resenias(2000, [user['user_id'] for user in range(5000)], vuelos)

    print("Carga de datos completa.")

# Ejecutar la carga de datos
if __name__ == "__main__":
    cargar_datos()
