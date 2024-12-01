import boto3
import time
import os
import funciones_bd

from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AMAZON_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')
AWS_REGION = os.getenv("aws_region")
STAGE = os.getenv("stage")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")

ATHENA_DATABASE = f'proyectofinal-{STAGE}-database'
ATHENA_TABLE = 'servicio-vuelos-v-dev-vuelos'
S3_OUTPUT_LOCATION = 's3://proyectofinal-dev-bucket-441925558343/'


client = boto3.client('athena', aws_access_key_id=AMAZON_ACCESS_KEY_ID, aws_secret_access_key=AMAZON_SECRET_ACCESS_KEY, region_name=AWS_REGION)

def run_athena_query(query, database, s3_output):
    
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database},
        ResultConfiguration={'OutputLocation': s3_output}
    )
    
    query_execution_id = response['QueryExecutionId']
    print(f"Query started with Execution ID: {query_execution_id}")
    
    while True:
        status = client.get_query_execution(QueryExecutionId=query_execution_id)
        state = status['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        print("Query is still running...")
        time.sleep(2)
    
    if state == 'SUCCEEDED':
        print("Query succeeded!")
    else:
        print(f"Query {state}: {status['QueryExecution']['Status']['StateChangeReason']}")
        return None
    
    results = client.get_query_results(QueryExecutionId=query_execution_id)
    return results

def fetch_results(results, max_rows=1000):
    rows = results['ResultSet']['Rows']
    data = []
    for row in rows[1:max_rows+1]:
        data.append([col.get('VarCharValue', None) for col in row['Data']])
    return data

def main():

    query = f'SELECT * FROM "{ATHENA_DATABASE}"."{ATHENA_TABLE}" LIMIT 1000'
    
    query_results = run_athena_query(query, ATHENA_DATABASE, S3_OUTPUT_LOCATION)
    
    if query_results:

        data = fetch_results(query_results)
        
        temp=[]

        print(data[0])

        for row in data: temp.append({
        "fecha_llegada":row[0],
        "destino":row[1],
        "tenant_id":row[2],
        "id_vuelo":row[3],
        "capacidad":row[4],
        "fecha_salida":row[5],
        "codigo":row[6],
        "origen":row[7]
        })
        
        funciones_bd.insert_multiple_rows_to_mysql("Vuelos",temp)
