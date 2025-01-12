import json
import mysql
from selenium.webdriver.common.by import By
from scrapper.brands import save_brand
from scrapper.categories import save_categories
from scrapper.db_utils import db_connection
from scrapper.images import save_images
from scrapper.prices import save_prices
from scrapper.specifications import save_specifications

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
    print("Marca ID:", brand_id)

    # salvar as categorias
    categories_saved = save_categories(product['categoria']['itemListElement'])
    print("Categorias: ", categories_saved)

    # salvar as especificações
    specifications_saved = save_specifications(specifications)
    print("Especificações: ", specifications_saved)

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
    print("Informações salvas com sucesso.")
    
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