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
    
def save_products_categories(categories_saved, product_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_insert_products_categories = """
            INSERT INTO products_categories (product_id, category_id, created_at)
            VALUES (%s, %s, NOW())
        """
        for category_id in categories_saved:
            product_category_data = (
                product_id,
                category_id,
            )
            if not check_if_product_category_exists(product_id, category_id):
                cursor.execute(sql_insert_products_categories, product_category_data)
            else:
                update_product_category(product_id, category_id)

        connection.commit()
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Erro ao salvar a relação entre produtos e categorias: {err}")
        return None
    
def check_if_product_category_exists(product_id, category_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_product_category = """
            SELECT id FROM products_categories WHERE product_id = %s AND category_id = %s
        """

        product_category_data = (
            product_id,
            category_id,
        )
        cursor.execute(sql_select_product_category, product_category_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:
        print(f"Erro ao verificar a relação entre produtos e categorias: {err}")
        return None
    
def update_product_category(product_id, category_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_update_product_category = """
            UPDATE products_categories
            SET updated_at = NOW()
            WHERE product_id = %s AND category_id = %s
        """
        product_category_data = (
            product_id,
            category_id,
        )
        cursor.execute(sql_update_product_category, product_category_data)

        connection.commit()
        cursor.close()
        connection.close()

        print("Relação entre produto e categoria atualizada com sucesso.")
        
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar a relação entre produtos e categorias: {err}")
        return None