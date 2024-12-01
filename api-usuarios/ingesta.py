import boto3
import pandas as pd
import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AMAZON_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AMAZON_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')
AWS_REGION = os.getenv("aws_region")
STAGE = os.getenv("stage")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")

NOMBRE_TABLA = "servicio-vuelos-dev-usuario"
S3_BUCKET_NAME = f"proyectofinal-{STAGE}-bucket-{ACCOUNT_ID}"
GLUE_DB = f"proyectofinal-{STAGE}-database"

dynamodb = boto3.client("dynamodb", aws_access_key_id=AMAZON_ACCESS_KEY_ID, aws_secret_access_key=AMAZON_SECRET_ACCESS_KEY, region_name=AWS_REGION)
s3 = boto3.client("s3", aws_access_key_id=AMAZON_ACCESS_KEY_ID, aws_secret_access_key=AMAZON_SECRET_ACCESS_KEY, region_name=AWS_REGION)
glue = boto3.client("glue", aws_access_key_id=AMAZON_ACCESS_KEY_ID, aws_secret_access_key=AMAZON_SECRET_ACCESS_KEY, region_name=AWS_REGION)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def infer_column_types(file_path):
    """Infers column types from a CSV file and returns a schema for Glue."""
    logger.info("Inferring column types from file: %s", file_path)
    df = pd.read_csv(file_path)

    type_mapping = {
        'int64': 'int',
        'float64': 'double',
        'object': 'string',
    }

    def detect_datetime_type(sample_values):
        for value in sample_values:
            if isinstance(value, str):
                if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', value):
                    return 'date'
                if re.match(r'^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}(:\d{1,2})?$', value):
                    return 'timestamp'
        return None

    columns = []
    for col_name, dtype in df.dtypes.items():
        glue_type = type_mapping.get(str(dtype), 'string')
        
        logger.debug("Column: %s, Inferred Type: %s", col_name, glue_type)
        
        if dtype == 'object':
            sample_values = df[col_name].dropna().astype(str).head(10)
            detected_type = detect_datetime_type(sample_values)
            if detected_type:
                glue_type = detected_type

        columns.append({"Name": col_name, "Type": glue_type})

    logger.info("Inferred columns: %s", columns)
    return columns

def scan_dynamodb_table():
    logger.info("Scanning DynamoDB table: %s", NOMBRE_TABLA)
    paginator = dynamodb.get_paginator("scan")
    response_iterator = paginator.paginate(TableName=NOMBRE_TABLA)

    items = []
    for page in response_iterator:
        items.extend(page.get("Items", []))
    logger.info("Retrieved %d items from DynamoDB", len(items))
    return items

def save_to_file(data, filename):
    logger.info("Saving data to file: %s", filename)
    df = pd.DataFrame([{k: list(v.values())[0] for k, v in item.items()} for item in data])
    df.to_csv(filename, index=False)
    logger.info("Data saved to file successfully")

def upload_to_s3(filename, bucket_name):
    logger.info("Uploading file to S3: %s/%s", bucket_name, filename)
    s3.upload_file(filename, bucket_name, "aerolineas/" + filename)
    logger.info("Uploaded %s to S3 bucket %s", filename, bucket_name)

def create_glue_catalog():
    logger.info("Creating Glue catalog")
    s3_path = f"s3://{S3_BUCKET_NAME}/aerolineas"

    columns = infer_column_types(NOMBRE_TABLA + ".csv")

    glue.create_table(
        DatabaseName=GLUE_DB,
        TableInput={
            "Name": NOMBRE_TABLA,
            "StorageDescriptor": {
                "Columns": columns,
                "Location": s3_path,
                "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                "SerdeInfo": {
                    "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                    "Parameters": {"field.delim": ","},
                },
            },
            "TableType": "EXTERNAL_TABLE",
        },
    )
    logger.info("Glue table '%s' created for data at %s", NOMBRE_TABLA, s3_path)

def main():
    logger.info("Starting main workflow")
    
    try:
    
        data = scan_dynamodb_table()

        filename = f"{NOMBRE_TABLA}.csv"
        save_to_file(data, filename)

        upload_to_s3(filename, S3_BUCKET_NAME)

        create_glue_catalog()

        os.remove(filename)
        logger.info("Temporary file '%s' removed", filename)
    
    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)

if __name__ == "__main__":
    main()
