from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from scrapper.images import get_images, download_and_upload_images
from scrapper.page import save_page
from scrapper.products import get_product_info, save_product
from scrapper.specifications import get_specifications
from scrapper.utils import scroll_page

BASE_URL = "https://www.lojasantoantonio.com.br/"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/165252-chocolate-granulado-ao-leite---granule-130g-melken---harald/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/chiclete-mentos-pure-fresh-sabor-morango-56g---van-melle-100855/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/33614-chiclete-plutonita-gelo-40un--arcor/p"
# BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/cake-box-quad-crist-ctpa-2l-165x165x8cm-6233-lsc-toys/p"

def main(): 
    driver = webdriver.Chrome()
    try:
        # Abrir a página
        driver.get(BASE_URL)
        # driver.get(BASE_URL_PRODUCT)
        sleep(5)
        
        menu_container = driver.find_element(By.CSS_SELECTOR, "ul.vtex-menu-2-x-menuContainer")  # Ajuste o seletor conforme necessário
        menu_items = menu_container.find_elements(By.CSS_SELECTOR, "li.vtex-menu-2-x-menuItem")
        
        for item in menu_items:
            # Simula hover para abrir submenus (se existirem)
            ActionChains(driver).move_to_element(item).perform()
            sleep(1)

            # Captura links nos submenus
            submenu_links = item.find_elements(By.CSS_SELECTOR, "a")
            for link in submenu_links:
                href = link.get_attribute("href")
                save_page(item.text, href)
        
        scroll_page(driver)

        # product = get_product_info(driver)
        # images = get_images(driver)
        # specifications = get_specifications(driver)
        
        # ftp_and_db_saved_images = []
        # if len(images) >= 1:
        #     ftp_and_db_saved_images = download_and_upload_images(images, product['produto'].get('sku'))
            
        # images_merged = [{"image": image, "url": url} for image, url in zip(ftp_and_db_saved_images, images)]

        # save_product(product, images_merged, specifications)
        
    finally:
        # Fechar o navegador
        driver.quit()

if __name__ == "__main__":
    load_dotenv()
    main()