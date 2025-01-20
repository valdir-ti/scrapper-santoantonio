from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from scrapper.images import get_images, download_and_upload_images
from scrapper.page import get_pages, get_total_pagination_from_page, save_page, update_total_pagination
from scrapper.products import get_product_info, get_products_links, save_product, save_product_link, update_product_link_error, update_product_link_read_field
from scrapper.specifications import get_specifications
from scrapper.utils import scroll_page

BASE_URL = "https://www.lojasantoantonio.com.br/"
BASE_URL_PRODUCT = "https://www.lojasantoantonio.com.br/165252-chocolate-granulado-ao-leite---granule-130g-melken---harald/p"

def main():
    driver = webdriver.Chrome()
    try:
        # driver.get(BASE_URL_PRODUCT)

        #####################
        # Salvei todas paginas com submenus e agora essa parte não vai ser mais usada
        # Abrir a página
        # driver.get(BASE_URL)
        # sleep(5)
        # scroll_page(driver)
        # menu_container = driver.find_element(By.CSS_SELECTOR, "ul.vtex-menu-2-x-menuContainer")  # Ajuste o seletor conforme necessário
        # menu_items = menu_container.find_elements(By.CSS_SELECTOR, "li.vtex-menu-2-x-menuItem")

        # for item in menu_items:
        #     # Simula hover para abrir submenus (se existirem)
        #     ActionChains(driver).move_to_element(item).perform()
        #     sleep(1)

        #     # Captura links nos submenus
        #     submenu_links = item.find_elements(By.CSS_SELECTOR, "a")
        #     for link in submenu_links:
        #         href = link.get_attribute("href")
        #         save_page(item.text, href)
        #####################

        #####################
        # Iterando sobre as paginas e salvando a quantidade de paginações que cada um tem
        # pages = get_pages()
        # for page in pages:
        #     url = page[0]
        #     page_id = page[1]
        #     driver.get(url)
        #     scroll_page(driver, 100, 0.1)
        #     sleep(5)

        #     total_pages = get_total_pagination_from_page(driver)
        #     print(page_id, url, total_pages)
        #     update_total_pagination(page_id, total_pages)
        #####################

        #####################
        # Iterar sobre as páginas novamente e agora ir paginando e salvando os produtos
        # pages = get_pages()
        # for page in pages:
        #     url = page[0]
        #     page_id = page[1]
        #     total_pagination = page[2]

        #     if total_pagination == 0:
        #         base_url = url
        #         driver.get(base_url)

        #         save_product_link(driver)

        #         ## Pegar os dados da pagina
        #         # product = get_product_info(driver)
        #         # images = get_images(driver)
        #         # specifications = get_specifications(driver)
        #         # print('0', product, specifications)

        #         scroll_page(driver, 10, 0.1)
        #         sleep(5)
        #     else:
        #         for pagination in range(1, total_pagination + 1):
        #             base_url = f"{url}?page={pagination}"
        #             driver.get(base_url)

        #             ## Pegar os dados da pagina
        #             # product = get_product_info(driver)
        #             # images = get_images(driver)
        #             # specifications = get_specifications(driver)
        #             # print('> 0', product, specifications)

        #             save_product_link(driver)

        #             scroll_page(driver, 10, 0.1)
        #             sleep(5)
        #####################



        #####################
        # Agora com os links de cada produto em mãos é hora de salvar cada um deles no processo

        products_link = get_products_links()

        for product_link in products_link:

            try:
                url = product_link[0]
                link_id = product_link[1]

                driver.get(url)
                sleep(4)
                scroll_page(driver, 10, 0.1)

                product = get_product_info(driver)

                if product is None or 'produto' not in product:
                    print(f"Produto não encontrado ou inválido para URL: {url}")
                    update_product_link_error(link_id)
                    with open('links.txt', 'a') as file:
                        file.write(f"{url}\n")
                    continue

                images = get_images(driver)
                specifications = get_specifications(driver)
                product_id = product['produto'].get('sku') if product['produto'].get('sku') else None
                print('trabalhando no produto: ', product_id, url)

                ftp_and_db_saved_images = []
                if len(images) >= 1:
                    ftp_and_db_saved_images = download_and_upload_images(images, product_id)

                images_merged = [{"image": image, "url": url} for image, url in zip(ftp_and_db_saved_images, images)]

                if (product_id):
                    save_product(product, images_merged, specifications)
                    update_product_link_read_field(link_id)
                else:
                    # Atualizar o campo de erro e salvar o link do produto em um txt
                    update_product_link_error(link_id)
                    with open('links.txt', 'a') as file:
                        file.write(f"{url}\n")

            except Exception as e:
                print(f"Erro ao processar URL {url}: {str(e)}")
                update_product_link_error(link_id)
                with open('links.txt', 'a') as file:
                    file.write(f"{url} - Erro: {str(e)}\n")
                continue
        #####################

    finally:
        # Fechar o navegador
        driver.quit()

if __name__ == "__main__":
    load_dotenv()
    main()