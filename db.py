import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='Desktop-VQ66B11J',
        port='3306',
        user='root',        
        password='Nath0853!',    
        database='MYSQL80'
    )
