import boto3
import random
import uuid
from datetime import datetime, timedelta
import hashlib
import os 
import csv
import json

# Configuración de DynamoDB
# Configuración de DynamoDB con credenciales
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-2',
    aws_access_key_id='',
    aws_secret_access_key='',
)

compras_table = "servicio-vuelos-compras-dev-compras"


def read_csv_to_json_array(file_path):
    """
    Reads a CSV file and converts it into an array of JSON objects.
    
    :param file_path: Path to the CSV file.
    :return: List of JSON objects (dictionaries).
    """
    json_array = []
    try:
        # Open the CSV file
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            # Create a CSV DictReader to automatically parse the header
            csv_reader = csv.DictReader(csv_file)
            
            # Iterate through the rows and append each as a dictionary to the list
            for row in csv_reader:
                json_array.append(row)
        
        return json_array
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

# Función para generar compras ficticias
def generar_compras(cantidad=10000, usuarios=[], vuelos=[]):
    print(f"Generando {cantidad} compras para {len(usuarios)} usuarios y {len(vuelos)} vuelos.")
    
    if not usuarios or not vuelos:
        print("Error: La lista de usuarios o la lista de vuelos está vacía.")
        return

    
    table_compras = dynamodb.Table(compras_table)
    """
    Genera `cantidad` de compras aleatorias.
    - `usuarios`: lista de user_id generados previamente.
    - `vuelos`: lista de id_vuelo generados previamente.
    """

    for _ in range(cantidad):
        try:
            # Crear datos aleatorios para la compra
            user_id = dict(random.choice(usuarios))["user_id"]
            id_vuelo = dict(random.choice(vuelos))["id_vuelo"]
            fecha_compra = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cantidad_boletos = random.randint(1, 5)  # Entre 1 y 5 boletos por compra
            precio_total = str(random.randint(50, 700))  # Precio por boleto entre $50 y $500

            # Crear el ítem para DynamoDB
            item = {
                'user_id': user_id,
                'id_compra': str(uuid.uuid4()),  # ID único de la compra
                'id_vuelo': id_vuelo,
                'fecha_compra': fecha_compra,
                'cantidad_boletos': cantidad_boletos,
                'precio_total': precio_total
            }

            # Insertar en DynamoDB
            table_compras.put_item(Item=item)
            print(f"Compra registrada: {item['id_compra']} para usuario {user_id} y vuelo {id_vuelo}")
        except Exception as e:
            print(f"Error al registrar compra: {e}")

# Example usage
file_path = "servicio-vuelos-v-dev-vuelos.csv"
json_data_vuelos = read_csv_to_json_array(file_path)

json_data_usuarios = read_csv_to_json_array("servicio-vuelos-dev-usuario.csv")

#print(json_data_usuarios)

generar_compras(cantidad=10000,usuarios=json_data_usuarios,vuelos=json_data_vuelos)