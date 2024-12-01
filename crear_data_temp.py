import boto3
import random
import os

from dotenv import load_dotenv
from faker import Faker

load_dotenv()

AMAZON_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AMAZON_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')

dynamodb = boto3.resource("dynamodb", aws_access_key_id=AMAZON_ACCESS_KEY_ID,aws_secret_access_key=AMAZON_SECRET_ACCESS_KEY,region_name="us-east-2")

fake = Faker()

def batch_write(table_name, generate_item_func, total_items=10000):
    
    table = dynamodb.Table(table_name)
    items = []
    
    for _ in range(total_items):
        items.append(generate_item_func())
        if len(items) == 25:  
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            items = []
    
    if items:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
    
    print(f"{total_items} registros insertados en la tabla {table_name}.")


def generate_airline():

    return {
        'aerolinea_id': fake.uuid4(),
        'aerolinea_nombre': fake.company(),
        'codigo': fake.lexify('??').upper(),
        'pais_origen': fake.country(),
        'precio':random.randint(1,10000),
        "fecha":f"{random.randint(11,30)}/{random.randint(10,12)}/2024"
    }

#z=generate_airline()
#print(z)

batch_write("aerolinea_temp",generate_airline,250)