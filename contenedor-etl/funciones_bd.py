import mysql.connector
from mysql.connector import Error

def insert_multiple_rows_to_mysql(table, rows_data):

    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="18.118.93.121",
            user="root",
            password="matias",
            database="gestion_vuelos"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()

            # Ensure all rows have the same keys (columns)
            if not rows_data:
                raise ValueError("No data to insert")

            columns = ', '.join(rows_data[0].keys())
            placeholders = ', '.join(['%s'] * len(rows_data[0]))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # Prepare values for all rows
            values = [tuple(row.values()) for row in rows_data]
            
            # Execute batch insert
            cursor.executemany(query, values)
            
            # Commit the transaction
            connection.commit()
            
            print(f"{cursor.rowcount} rows inserted successfully into table {table}")
            return True

    except Error as e:
        print(f"Error: {e}")
        return False

    finally:
        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
