import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

BASE_URL = "https://www.lojasantoantonio.com.br/"
BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/cake-box-quad-crist-ctpa-2l-165x165x8cm-6233-lsc-toys/p"
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

def get_especifications(driver):
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
        especifications = get_especifications(driver)
        
        print(product['produto'])
        print(product['categoria'])
        print(images)
        print(especifications)

    finally:
        # Fechar o navegador
        driver.quit()

if __name__ == "__main__":
    main()