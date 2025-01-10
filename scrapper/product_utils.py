import json
from selenium.webdriver.common.by import By

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

def save_product(product, images, specifications):
    # Salvar as informações na base de dados
    print("Salvando informações na base de dados...")
    
    # salvar as marcas
    
    # salvar as categorias
    
    # salvar os produtos

    # Exemplo de uso
    print(product['produto'])
    print(product['categoria'])
    print(images)
    print(specifications)

    print("Informações salvas com sucesso.")