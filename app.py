from dotenv import load_dotenv
import json
import os
import requests
from ftplib import FTP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

BASE_URL = "https://www.lojasantoantonio.com.br/"
BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/165252-chocolate-granulado-ao-leite---granule-130g-melken---harald/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/chiclete-mentos-pure-fresh-sabor-morango-56g---van-melle-100855/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/cake-box-quad-crist-ctpa-2l-165x165x8cm-6233-lsc-toys/p"

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

def sanitize_filename(url, product_id, index):
    print("sanitize => ", url)
    """
    Gera um nome de arquivo padronizado com base no ID do produto e no índice.
    Exemplo: 11212313-1.jpg
    """
    # Extrair a extensão do arquivo (ex: .jpg, .png)
    extension = os.path.splitext(url.split("?")[0])[-1]
    
    # Se não tiver extensão, adiciona .jpg por padrão
    if not extension:
        extension = '.jpg'

    return f"{product_id}-{index}{extension}"

def download_and_upload_images(image_urls, product_id, ftp_host, ftp_user, ftp_password, ftp_folder):
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
    
    # Fazer o download das imagens e enviá-las para o FTP
    for index, url in enumerate(image_urls, start=1):
        file_name = sanitize_filename(url, product_id, index)  # Extrair o nome do arquivo da URL
        print(f"Baixando {url}...")
        
        # Baixar a imagem
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            local_file_path = os.path.join("./temp", file_name)
            
            # Garantir que o diretório local temporário existe
            os.makedirs("./temp", exist_ok=True)
            
            # Salvar a imagem localmente
            with open(local_file_path, 'wb') as local_file:
                for chunk in response.iter_content(1024):
                    local_file.write(chunk)
            
            print(f"{file_name} baixado. Enviando para o FTP...")
            
            # Enviar para o FTP
            with open(local_file_path, 'rb') as file:
                ftp.storbinary(f"STOR {file_name}", file)
            
            print(f"{file_name} enviado para o FTP.")
            
            # Remover o arquivo local temporário
            os.remove(local_file_path)
        else:
            print(f"Erro ao baixar {url}: {response.status_code}")
    
    # Fechar conexão FTP
    ftp.quit()
    print("Conexão FTP encerrada.")

def scroll_page(driver):
    for _ in range(16):  # Número de vezes que deseja rolar (10 * 100px = 1000px)
        driver.execute_script("window.scrollBy(0, 60);")
        sleep(0.5)  # Pausa de 0.5s entre os scrolls para simular comportamento humano
    
def main(): 
    driver = webdriver.Chrome()
    try:
        # Abrir a página
        driver.get(BASE_URL_PRODUCT)
        sleep(5)

        scroll_page(driver)

        product = get_product_info(driver)
        images = get_images(driver)
        specifications = get_specifications(driver)
        
        # print(product['produto'])
        # print(images)
        
        # Exemplo de uso
        ftp_host = os.getenv('FTP_HOST')
        ftp_user = os.getenv('FTP_USER')
        ftp_password = os.getenv('FTP_PASS')
        ftp_folder = "/santo-antonio/images"
        download_and_upload_images(images, product['produto'].get('sku'), ftp_host, ftp_user, ftp_password, ftp_folder)
        
        # print(product['produto'])
        # print(product['categoria'])
        # print(images)
        # print(specifications)

    finally:
        # Fechar o navegador
        driver.quit()

if __name__ == "__main__":
    load_dotenv()
    main()