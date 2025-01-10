import os
import requests
from ftplib import FTP
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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