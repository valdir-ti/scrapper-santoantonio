import mysql
from scrapper.db_utils import db_connection
from datetime import datetime

def save_prices(product):
    try:
        connection = db_connection()
        cursor = connection.cursor()
        
        sql_insert_price = """
            INSERT INTO prices (product_id, lowPrice, highPrice, price, priceCurrency, priceValidUntil, created_at)
            VALUES (%s, %s, %s, %s,%s, %s, NOW())
        """
        
        product_id = product['produto']['sku']
        priceValidUntilIso = product['produto']['offers']['offers'][0]['priceValidUntil']
        lowPrice = product['produto']['offers']['lowPrice']
        highPrice = product['produto']['offers']['highPrice']
        price = product['produto']['offers']['offers'][0]['price']
        priceCurrency = product['produto']['offers']['offers'][0]['priceCurrency']
        formatted_date = datetime.strptime(priceValidUntilIso, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')

        price_data = (
            product_id,
            lowPrice,
            highPrice,
            price,
            priceCurrency,
            formatted_date,
        )
        
        if not check_if_price_exists(product_id):
            cursor.execute(sql_insert_price, price_data)
        else:
            update_price(product)
        
        connection.commit()
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Erro ao salvar o preço: {err}")
        return None
    
def check_if_price_exists(product_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()
        
        sql_select_price = """
            SELECT id FROM prices WHERE product_id = %s
        """
        price_data = (
            product_id,
        )
        
        cursor.execute(sql_select_price, price_data)    
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            return result[0]
        
        return None
    
    except mysql.connector.Error as err:
        print(f"Erro ao verificar o preço: {err}")
        return None
    
def update_price(product):
    try:
        connection = db_connection()
        cursor = connection.cursor()
        
        sql_update_price = """
            UPDATE prices
            SET lowPrice = %s, highPrice = %s, price = %s, priceCurrency = %s, priceValidUntil = %s, updated_at = NOW()
            WHERE product_id = %s
        """
        
        product_id = product['produto']['sku']
        priceValidUntilIso = product['produto']['offers']['offers'][0]['priceValidUntil']
        formatted_date = datetime.strptime(priceValidUntilIso, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
        lowPrice = product['produto']['offers']['lowPrice']
        highPrice = product['produto']['offers']['highPrice']
        price = product['produto']['offers']['offers'][0]['price']
        priceCurrency = product['produto']['offers']['offers'][0]['priceCurrency']
        
        price_data = (
            lowPrice,
            highPrice,
            price,
            priceCurrency,
            formatted_date,
            product_id,
        )
        
        cursor.execute(sql_update_price, price_data)
        
        connection.commit()
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o preço: {err}")
        return None