import json
from selenium.webdriver.common.by import By
from scrapper.brand import save_brand
from scrapper.categories import save_categories
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
    print(images)
    
    # salvar as marcas
    brand = product['produto']['brand'].get('name')
    brand_id = save_brand(brand)
    print("Marca ID:", brand_id)

    # salvar as categorias
    # depois de salvar o produto, salvar as essas categorias na tabela products_categories
    categories_saved = save_categories(product['categoria']['itemListElement'])
    print("Categorias: ", categories_saved)
    
    # salvar as especificações
    specifications_saved = save_specifications(specifications)
    print("Especificações: ", specifications_saved)
    
    # salvar as imagens

    # salvar o produto

    # Exemplo de uso
    # print(product['produto'])
    # print(images)
    # print(specifications)
    print("Informações salvas com sucesso.")