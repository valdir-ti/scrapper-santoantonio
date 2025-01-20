import mysql
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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

def get_pages():
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_pages = """
            SELECT url, id, total_pages FROM pages
        """

        cursor.execute(sql_select_pages)

        pages = cursor.fetchall()

        cursor.close()
        connection.close()

        return pages

    except mysql.connector.Error as err:
        print(f"Erro ao buscar as páginas: {err}")
        return None

def update_total_pagination(page_id, total_pages):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_update_total_pagination = """
            UPDATE pages
            SET total_pages = %s, updated_at = NOW()
            WHERE id = %s
        """
        total_pagination_data = (
            total_pages,
            page_id,
        )
        cursor.execute(sql_update_total_pagination, total_pagination_data)

        connection.commit()
        cursor.close()
        connection.close()
        return

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o total de paginas: {err}")
        return None

def get_total_pagination_from_page(driver):
    try:

        try:
            pagination_container = driver.find_element(
                By.CLASS_NAME,
                "lojasantoantonio-search-result-custom-0-x-buttonShowMore"
            )
        except NoSuchElementException:
            return 0  # Retorna 0 se o container de paginação não for encontrado

        # Tentar localizar os itens de paginação dentro do container
        try:
            pagination_items = pagination_container.find_elements(
                By.CLASS_NAME,
                "lojasantoantonio-search-result-custom-0-x-buttonShowMorePaginationCustom"
            )
        except NoSuchElementException:
            return 0

        return len(pagination_items) if pagination_items else 0

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o total de paginas: {err}")
        return None