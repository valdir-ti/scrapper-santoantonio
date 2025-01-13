import mysql
from scrapper.db_utils import db_connection

def save_page(page_type, page_url):
    try:
        connection = db_connection()
        cursor = connection.cursor()
        
        sql_insert_page = """
            INSERT INTO pages (type, url, created_at)
            VALUES (%s, %s, NOW())
        """
        page_data = (
            page_type,
            page_url,
        )
        cursor.execute(sql_insert_page, page_data)
        
        connection.commit()
        cursor.close()
        connection.close()                
        
    except mysql.connector.Error as err:
        print(f"Erro ao salvar a página: {err}")
        return None
    
    
    
    