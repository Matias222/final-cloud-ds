from mysql.connector import Error
from dotenv import load_dotenv

import mysql.connector
import os

load_dotenv()

HOST = os.getenv('MYSQL_DB_URL')
DATABASE = os.getenv('MYSQL_DATABASE')
USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASSWORD')

def run_sql_script(sql_file="./init.sql"):
    try:
        connection = mysql.connector.connect(
            host=HOST,
            database=DATABASE,
            user=USER,
            password=PASSWORD
        )

        if connection.is_connected():
            cursor = connection.cursor()
            with open(sql_file, 'r') as file:
                sql_script = file.read()

            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)

            connection.commit()
            cursor.close()
            print(f"SQL script {sql_file} executed successfully.")
    
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if connection.is_connected():
            connection.close()
            print("Connection closed.")



run_sql_script()
