import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

BASE_URL = "https://www.lojasantoantonio.com.br/"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/cake-box-quad-crist-ctpa-2l-165x165x8cm-6233-lsc-toys/p"
BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/cake-box-quad-crist-ctpa-2l-165x165x8cm-6233-lsc-toys/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/chiclete-mentos-pure-fresh-sabor-morango-56g---van-melle-100855/p"

def main(): 
    driver = webdriver.Chrome()
    try:
        # Abrir a página
        driver.get(BASE_URL_PRODUCT)
        sleep(5)
        
        swiper_wrapper = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "swiper-wrapper"))
        )

        script_tags = driver.find_elements("xpath", "//script[@type='application/ld+json']")

        # Verificar se há pelo menos duas tags
        if len(script_tags) >= 2:

            # Capturar o conteúdo JSON da primeira tag (Produto)
            json_produto = script_tags[0].get_attribute("innerHTML")
            # Capturar o conteúdo JSON da segunda tag (Categoria)
            json_categoria = script_tags[1].get_attribute("innerHTML")

            ### Buscar as imagens do produto
            container = driver.find_element(By.XPATH, "//div[@data-testid='thumbnail-swiper']")        
            
            # Capturar todas as tags <figure> dentro do contêiner
            figures = container.find_elements(By.TAG_NAME, "figure")

            # Criar um array para armazenar os links das imagens
            image_links = []

            for figure in figures:
                # Localizar a tag <img> dentro da <figure>
                img = figure.find_element(By.TAG_NAME, "img")
                img_src = img.get_attribute("src")  # Capturar o atributo 'src' da tag <img>
                
                # Adicionar o link ao array
                image_links.append(img_src)
                
            # Capturar as divs filhas diretamente
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

            try:
                # Converter os conteúdos para objetos Python
                produto = json.loads(json_produto)
                categoria = json.loads(json_categoria)

                # Exibir os resultados
                print("Produto:")
                print(json.dumps(produto, indent=4, ensure_ascii=False))
                print("\nCategoria:")
                print(json.dumps(categoria, indent=4, ensure_ascii=False))
                print("\nImagens:")
                print(image_links)
            
            except json.JSONDecodeError as e:
                print("Erro ao decodificar o JSON:", e)

    finally:
        # Fechar o navegador
        driver.quit()

if __name__ == "__main__":
    main()