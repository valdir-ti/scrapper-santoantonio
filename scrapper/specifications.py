import mysql
from selenium.webdriver.common.by import By

from scrapper.db_utils import db_connection

def get_specifications(driver):
    # Localizar filhas diretas
    child_divs = driver.find_elements(
        By.CSS_SELECTOR,
        ".lojasantoantonio-especification-product-0-x-wrapper--product-especification.lojasantoantonio-especification-product-0-x-wrapper--product-especification--wrapper--accordion-product-image > div"
    )
    
    result = []
    
    for div in child_divs:
        # Obter o botão com o h2
        try:
            button = div.find_element(By.CSS_SELECTOR, "button")
            h2_text = button.find_element(By.CSS_SELECTOR, "h2").text
        except Exception as e:
            h2_text = None

        # Obter o texto do span
        try:
            span = div.find_element(By.CSS_SELECTOR, "span")
            span_text = span.get_attribute("outerHTML")  # Inclui o HTML completo do span
        except Exception as e:
            span_text = None
        
        # Adicionar as informações ao resultado
        result.append({
            "header": h2_text,
            "content": span_text
        })
    return result

def save_specifications(specifications):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_insert_specification = """
            INSERT INTO specifications (header, content, created_at)
            VALUES (%s, %s, NOW())
        """
        specifications_ids = []
        for specification in specifications:
            header = specification.get('header')
            content = specification.get('content')
            
            id_specification_exists = check_if_specification_exists(header, content)
            if id_specification_exists:
                specifications_ids.append(id_specification_exists)
                continue
            
            specification_data = (
                header,
                content,
            )
            cursor.execute(sql_insert_specification, specification_data)
            specifications_ids.append(cursor.lastrowid)

        # Confirmar as mudanças no banco de dados
        connection.commit()
        cursor.close()
        connection.close()
        return specifications_ids
    
    except mysql.connector.Error as err:
        print(f"Erro ao salvar a especificação: {err}")
        return None
    
def check_if_specification_exists(header, content):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_specification = """
            SELECT id FROM specifications WHERE header = %s AND content = %s
        """

        specification_data = (
            header,
            content,
        )
        cursor.execute(sql_select_specification, specification_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:
        print(f"Erro ao verificar a especificação: {err}")
        return None