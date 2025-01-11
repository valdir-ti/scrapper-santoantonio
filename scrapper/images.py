import os
import mysql
import requests
from ftplib import FTP
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapper.db_utils import db_connection
from scrapper.ftp_utils import connect_ftp
from scrapper.utils import sanitize_filename

def get_images(driver):
    # Capturar o contêiner das imagens
    swiper_wrapper = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "swiper-wrapper"))
    )
    swiper_slides = swiper_wrapper.find_elements(By.CLASS_NAME, "swiper-slide")

    # Criar uma lista para armazenar os links das imagens
    image_links = []

    # Iterar por cada slide para capturar as imagens
    for slide in swiper_slides:
        try:
            # Localizar a tag <img> dentro do slide
            img = slide.find_element(By.TAG_NAME, "img")
            # Capturar o atributo 'src'
            img_src = img.get_attribute("src")
            # Adicionar o link à lista
            image_links.append(img_src)
        except Exception as e:
            print(f"Erro ao capturar imagem no slide: {e}")
    return image_links

def download_and_upload_images(image_urls, product_id):
    ftp_config = connect_ftp()
    ftp_host = ftp_config['ftp_host']
    ftp_user = ftp_config['ftp_user']
    ftp_password = ftp_config['ftp_password']
    ftp_folder = ftp_config['ftp_folder']

    # Conectar ao servidor FTP
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)
    print(f"Conectado ao FTP: {ftp_host}")

    # Criar o diretório no FTP, se não existir
    try:
        ftp.cwd(ftp_folder)
    except:
        ftp.mkd(ftp_folder)
        ftp.cwd(ftp_folder)

    images_ftp_saved = []
    for index, url in enumerate(image_urls, start=1):
        file_name = sanitize_filename(url, product_id, index)  # Extrair o nome do arquivo da URL
        print(f"Baixando {url}...")

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            local_file_path = os.path.join("./temp", file_name)

            os.makedirs("./temp", exist_ok=True)

            with open(local_file_path, 'wb') as local_file:
                for chunk in response.iter_content(1024):
                    local_file.write(chunk)

            print(f"{file_name} baixado. Enviando para o FTP...")
            images_ftp_saved.append(file_name)

            with open(local_file_path, 'rb') as file:
                ftp.storbinary(f"STOR {file_name}", file)

            print(f"{file_name} enviado para o FTP.")
            os.remove(local_file_path)
        else:
            print(f"Erro ao baixar {url}: {response.status_code}")

    ftp.quit()
    print("Conexão FTP encerrada.")
    return images_ftp_saved

def save_images(images, product_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_insert_image = """
            INSERT INTO images (image, url, created_at)
            VALUES (%s, %s, NOW())
        """

        for image in images:
            img_name = image['image']
            url = image['url']

            id_image_exists = check_if_image_exists(img_name, url)
            if id_image_exists:
                if not check_if_products_images_exists(product_id, id_image_exists):
                    save_products_images(product_id, id_image_exists)
            else:
                image_data = (
                    img_name,
                    url,
                )
                cursor.execute(sql_insert_image, image_data)
                last_inserted_image_id = cursor.lastrowid
                if not check_if_products_images_exists(product_id, last_inserted_image_id):
                    save_products_images(product_id, last_inserted_image_id)

        connection.commit()
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Erro ao salvar a imagem: {err}")
        return None

def save_products_images(product_id, image_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_insert_product_image = """
            INSERT INTO products_images (product_id, image_id, created_at)
            VALUES (%s, %s, NOW())
        """

        image_data = (
            product_id,
            image_id,
        )
        cursor.execute(sql_insert_product_image, image_data)

        connection.commit()
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Erro ao salvar a imagem do produto: {err}")
        return None
    
def check_if_products_images_exists(product_id, image_id):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_product_image = """
            SELECT id FROM products_images WHERE product_id = %s AND image_id = %s
        """

        product_image_data = (
            product_id,
            image_id,
        )
        cursor.execute(sql_select_product_image, product_image_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:
        print(f"Erro ao verificar a imagem do produto: {err}")
        return None

def check_if_image_exists(image, url):
    try:
        connection = db_connection()
        cursor = connection.cursor()

        sql_select_image = """
            SELECT id FROM images WHERE image = %s AND url = %s
        """

        image_data = (
            image,
            url,
        )
        cursor.execute(sql_select_image, image_data)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]

        return None

    except mysql.connector.Error as err:
        print(f"Erro ao verificar a imagem: {err}")
        return None