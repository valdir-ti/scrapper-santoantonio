import json
import mysql
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapper.brands import save_brand
from scrapper.categories import save_categories, save_products_categories
from scrapper.db_utils import db_connection
from scrapper.images import save_images
from scrapper.prices import save_prices
from scrapper.specifications import save_products_specifications, save_specifications

def save_product_link(driver):
    try:
        links = driver.find_elements("xpath", "//div[@id='gallery-layout-container']/div//a[1]")
        for link in links:
            href = link.get_attribute("href")
            connection = db_connection()
            cursor = connection.cursor()

            sql_insert_product_link = """
                INSERT INTO product_link (link, created_at)
                VALUES (%s, NOW())
            """
            page_data = (href,)
            cursor.execute(sql_insert_product_link, page_data)

            connection.commit()
            cursor.close()
            connection.close()

    except mysql.connector.Error as err:
        print(f"Erro ao salvar o link do produto: {err}")

def get_products_links():
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_product_link = """
            SELECT a.link, a.id, a.`read`, MIN(a.created_at) as created_at
            FROM product_link a
            WHERE 1=1 AND a.`read` = 0
            GROUP BY a.link
        """

        product_data = ()
        cursor.execute(sql_select_product_link, product_data)

        result = cursor.fetchall()

        cursor.close()
        connection.close()

        if result:
            return result

        return None

    except mysql.connector.Error as err:
        print(f"Erro ao buscar o link do produto: {err}")


def get_product_info(driver):

    script_tags = driver.find_elements("xpath", "//script[@type='application/ld+json']")

    # Verificar se há pelo menos duas tags
    if len(script_tags) >= 2:

        # Capturar o conteúdo JSON da primeira tag (Produto)
        json_produto = script_tags[0].get_attribute("innerHTML")
        # Capturar o conteúdo JSON da segunda tag (Categoria)
        json_categoria = script_tags[1].get_attribute("innerHTML")

        # Converter os conteúdos para objetos Python
        produto = json.loads(json_produto)
        categoria = json.loads(json_categoria)

        return {
            "produto": produto,
            "categoria": categoria,
        }

    return None

def save_product(product, images, specifications):
    # salvar as marcas
    brand = product['produto']['brand'].get('name')
    brand_id = save_brand(brand)

    # salvar as categorias
    categories_saved = save_categories(product['categoria']['itemListElement'])

    # salvar as especificações
    specifications_saved = save_specifications(specifications)

    # salvar as imagens
    save_images(images, product['produto']['sku'])

    # salvar o produto
    connection = db_connection()
    cursor = connection.cursor()

    sql_insert_product = """
        INSERT INTO products (product_id, link, name, mpn, sku, ean, brand_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """

    product_data = (
        product['produto']['sku'],
        product['produto']['@id'],
        product['produto']['name'],
        product['produto']['mpn'],
        product['produto']['sku'],
        product['produto']['gtin'],
        brand_id,
    )

    if not check_if_product_exists(product['produto']['sku']):
        cursor.execute(sql_insert_product, product_data)
    else:
        update_product(product, brand_id)

    connection.commit()
    cursor.close()
    connection.close()

    # salvar os prices
    save_prices(product)

    #salvar especificações do produto
    save_products_specifications(specifications_saved, product['produto']['sku'])

    # salvar as categorias do produto
    save_products_categories(categories_saved, product['produto']['sku'])

    print("Informações salvas com sucesso.")
    
def update_product_link_read_field(link_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()
        
        sql_update_read_field = """
            UPDATE product_link SET `read` = 1, updated_at = NOW()
            WHERE id = %s
        """
        
        product_data = (
            link_id,
        )
        
        cursor.execute(sql_update_read_field, product_data)        
        
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Campo read do produto atualizado com sucesso")
        
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o campo read do produto: {err}")
        return None

def update_product_link_error(link_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()
        
        sql_update_read_field = """
            UPDATE product_link SET `read` = 1, error_redirect = 1, updated_at = NOW()
            WHERE id = %s
        """
        
        product_data = (
            link_id,
        )
        
        cursor.execute(sql_update_read_field, product_data)        
        
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Campo read do produto atualizado com sucesso")
        
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o campo error redirect do produto: {err}")
        return None
        

def update_product(product, brand_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_update_product = """
            UPDATE products SET name = %s, link = %s, mpn = %s, ean = %s, brand_id = %s, updated_at = NOW()
            WHERE product_id = %s
        """

        product_data = (
            product['produto']['name'],
            product['produto']['@id'],
            product['produto']['mpn'],
            product['produto']['gtin'],
            product['produto']['sku'],
            brand_id,
        )
        cursor.execute(sql_update_product, product_data)

        connection.commit()
        cursor.close()
        connection.close()

        print("Produto atualizado com sucesso.")

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o produto: {err}")
        return None

def check_if_product_exists(product_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_product = """
            SELECT id FROM products WHERE product_id = %s
        """

        product_data = (
            product_id,
        )
        cursor.execute(sql_select_product, product_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:
        print(f"Erro ao verificar o produto: {err}")
        return None