from dotenv import load_dotenv
from selenium import webdriver
from time import sleep
from scrapper.images import get_images, download_and_upload_images
from scrapper.products import get_product_info, save_product
from scrapper.specifications import get_specifications
from scrapper.utils import scroll_page

BASE_URL = "https://www.lojasantoantonio.com.br/"
BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/165252-chocolate-granulado-ao-leite---granule-130g-melken---harald/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/chiclete-mentos-pure-fresh-sabor-morango-56g---van-melle-100855/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/33614-chiclete-plutonita-gelo-40un--arcor/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/cake-box-quad-crist-ctpa-2l-165x165x8cm-6233-lsc-toys/p"

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
        
        ftp_and_db_saved_images = []
        if len(images) >= 1:
            ftp_and_db_saved_images = download_and_upload_images(images, product['produto'].get('sku'))
            
        images_merged = [{"image": image, "url": url} for image, url in zip(ftp_and_db_saved_images, images)]

        save_product(product, images_merged, specifications)
        
    finally:
        # Fechar o navegador
        driver.quit()

if __name__ == "__main__":
    load_dotenv()
    main()