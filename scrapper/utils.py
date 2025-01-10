import os
from time import sleep

def sanitize_filename(url, product_id, index):
    # Extrair a extensão do arquivo (ex: .jpg, .png)
    extension = os.path.splitext(url.split("?")[0])[-1]
    
    # Se não tiver extensão, adiciona .jpg por padrão
    if not extension:
        extension = '.jpg'

    return f"{product_id}-{index}{extension}"

def scroll_page(driver):
    for _ in range(16):  # Número de vezes que deseja rolar (10 * 100px = 1000px)
        driver.execute_script("window.scrollBy(0, 60);")
        sleep(0.5)  # Pausa de 0.5s entre os scrolls para simular comportamento humano