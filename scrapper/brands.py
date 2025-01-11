import mysql
from scrapper.db_utils import db_connection

def save_brand(brand):
    
    brand_exists = check_brand_exists(brand)
    if brand_exists:
        return brand_exists
    
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_insert_brand = """
            INSERT INTO brands (brand, created_at)
            VALUES (%s, NOW())
        """

        brand_data = (
            brand,
        )
        cursor.execute(sql_insert_brand, brand_data)

        # Confirmar as mudanças no banco de dados
        connection.commit()
        cursor.close()
        connection.close()

        return cursor.lastrowid

    except mysql.connector.Error as err:  # Captura erros do MySQL
        print(f"Erro ao salvar a marca: {err}")

def check_brand_exists(brand):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_brand = """
            SELECT id FROM brands WHERE brand = %s
        """

        brand_data = (
            brand,
        )
        cursor.execute(sql_select_brand, brand_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:  # Captura erros do MySQL
        print(f"Erro ao verificar a marca: {err}")
        return None