import mysql
from scrapper.db_utils import db_connection

def save_categories(categories):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_insert_category = """
            INSERT INTO categories (position, name, item, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        categories_ids = []
        for category in categories:
            
            id_category_exists = check_if_category_exists(category.get('name'))
            if id_category_exists:
                categories_ids.append(id_category_exists)
                continue
            
            position = category.get('position')
            name = category.get('name')
            item = category.get('item')
            category_data = (
                position,
                name,
                item,
            )
            cursor.execute(sql_insert_category, category_data)
            categories_ids.append(cursor.lastrowid)

        # Confirmar as mudanças no banco de dados
        connection.commit()
        cursor.close()
        connection.close()
        return categories_ids

    except mysql.connector.Error as err:  # Captura erros do MySQL
        print(f"Erro ao salvar a categoria: {err}")
    
def check_if_category_exists(category):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_category = """
            SELECT id FROM categories WHERE name = %s
        """

        category_data = (
            category,
        )
        cursor.execute(sql_select_category, category_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:  # Captura erros do MySQL
        print(f"Erro ao verificar a categoria: {err}")
        return None