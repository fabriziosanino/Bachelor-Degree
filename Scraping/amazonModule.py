from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait

"""Apre la schermata principale e naviga sul prodotto passato come parametro

Parametri
----------
driver : seleniumDriver
    Scheda di chrome in cui navigare
productName : string
    Prodotto da inserire nella barra di ricerca

Returns
-------
    Niente
"""
def navigateToProducts(driver, productName):
    linkAmazon = 'https://www.amazon.com'
    driver.get(linkAmazon)

    driver.implicitly_wait(1)
    search = driver.find_element(By.ID, 'twotabsearchtextbox')
    search.send_keys(productName)
    search.send_keys(Keys.ENTER)

    driver.implicitly_wait(0.5)


"""Raccoglie in una lista tutti i prodotti che sono presenti nella pagina

Parametri
----------
driver : seleniumDriver
    Scheda di chrome in cui navigare

Returns
-------
list
    Lista di prodotti
"""
def getProducts(driver):
    items = wait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@data-component-type, "s-search-result")]')))

    return items


"""Ottiene il link della prossima pagina di prodotti

Parametri
----------
driver : seleniumDriver
    Scheda di chrome in cui navigare

Returns
-------
string
    Link della prossima pagina
"""
def getLinkNextPage(driver):
    linkNextPage = wait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH,
                                             '//span[@class="s-pagination-strip"]/a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]')))
    linkNextPage = linkNextPage[0].get_attribute("href")

    return linkNextPage


"""Ottiene il nome del prodotto. Quello contenuto nella descrizione principale

Parametri
----------
item: prodotto
    Prodotto in cui cercare il nome

Returns
-------
string
    Nome del prodotto
"""
def getProductName(item):
    productName = ""
    try:
        productName = item.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')
    except:
        # ALCUNI PRODOTTI COPRONO UNA RIGA INTERA
        productName = item.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]')

    return productName


"""Ottiene il prezzo del prodotto

Parametri
----------
item: prodotto
    Prodotto in cui cercare il prezzo

Returns
-------
string
    Prezzo del prodotto
"""
def getProductPrice(item):
    try:
        productPrice = item.find_element(By.XPATH, './/span[@class="a-offscreen"]').get_attribute("innerHTML")
    except:
        productPrice = ""

    return productPrice


"""Ottiene il link alla pagina del prodotto

Parametri
----------
item: prodotto
    Prodotto in cui cercare il link

Returns
-------
string
    Link del prodotto
"""
def getLinkProduct(item):
    linkProduct = item.find_element(By.XPATH,
                                    './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')

    return linkProduct


"""Ottiene il link all'immagine del prodotto

Parametri
----------
item: prodotto
    Prodotto in cui cercare il link

Returns
-------
string
    Link all'immagine
"""
def getLinkProductImg(item):
    imageProduct = item.find_element(By.XPATH, './/img[@class="s-image"]')

    return imageProduct


"""
Aggiunge alla string passata come parametro, il contenuto di tutti i tag presenti nella lista itemsFind
"""
def appendTextDetails(itemsFind, text):
    for item in itemsFind:
        text += "-" + item.text

    return text


"""Ottiene tutti i dettagli del prodotto contenuti nella pagina di esso

Parametri
----------
driver : seleniumDriver
    Scheda di chrome in cui navigare
linkProduct: string
    Link al prodotto di cui si vogliono ottenere i dettagli
textToSearch: string
    Conterrà i dettagli del prodotto

Returns
-------
string
    Concatenazione di tutti i dettagli
"""
def getProductDetails(driver, linkProduct, textToSearch):
    # Utilizzo l'instanza di google chrome per cercare il prodotto
    driver.get(linkProduct.get_attribute("href"))
    driver.implicitly_wait(0.5)

    externalContainer = wait(driver, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'featurebullets_feature_div')))
    infos = externalContainer[0].find_elements(By.XPATH, './/span[@class="a-list-item"]')

    # Metto in una stringa comune tutte le descrizioni in modo da fare la ricerca in modo più veloce
    textToSearch = appendTextDetails(infos, textToSearch)

    try:
        descriptions = wait(driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, 'productDescription')))
        p = descriptions[0].find_element(By.TAG_NAME, 'p')  # TODO: CONTROLLARE SE POSSONO ESSERE PRESENTI PIU P
        textToSearch += "-" + p.text
    except:
        # ALCUNI PRODOTTI NON HANNO LA DESCRIZIONE
        None
    finally:
        # Controllo se sono presenti tutte le caratteristiche richieste

        try:
            detailsTable = wait(driver, 10).until(
                EC.presence_of_all_elements_located((By.ID, 'productDetails_techSpec_section_1')))
            details = detailsTable[0].find_elements(By.XPATH, './/td["a-size-base prodDetAttrValue"]')

            textToSearch = appendTextDetails(details, textToSearch)
        except:
            # ALCUNI PRODOTTI NON HANNO LA TABELLA DEI DETTAGLI
            None

    return textToSearch
