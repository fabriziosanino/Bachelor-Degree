from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait

import scrapingModuleAbstract

class AmazonModule(scrapingModuleAbstract.AbstractModule):
    """Apre la schermata principale e naviga sul prodotto passato come parametro

    Parametri
    ----------
    driver : seleniumDriver
        Scheda di chrome in cui navigare
    productName : string
        Prodotto da inserire nella barra di ricerca

    Returns
    -------
    """
    def navigateToProducts(self, driver, productName):
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
    def getProducts(self, driver):
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
    def getLinkNextPage(self, driver):
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
    def getProductName(self, item):
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
    def getProductPrice(self, item):
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
    def getLinkProduct(self, item):
        linkProduct = item.find_element(By.XPATH,
                                        './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')

        return linkProduct


    """Ottiene il rating del prodotto definito da Amazon
    
    Parametri
    ----------
    item: prodotto
        Prodotto in cui cercare il rating
    
    Returns
    -------
    string
        Rating del prosotto
    """
    def getProductReviewRating(self, item):
        try:
            rating = item.find_element(By.XPATH,
                                            './/span[@class="a-icon-alt"]').get_attribute("innerHTML")

            rating = rating.split(' out')[0]
        except:
            #Alcuni prodotti non hanno alcuna recensione
            rating = 0

        return rating


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
    def getLinkProductImg(self, item):
        imageProduct = item.find_element(By.XPATH, './/img[@class="s-image"]')

        return imageProduct


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
    def getProductDetails(self, driver, linkProduct, textToSearch):
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


    """Ottiene il link all'immagine del prodotto
    
    Parametri
    ----------
    driver : seleniumDriver
        Scheda di chrome in cui navigare
    
    Returns
    -------
    string, Optional
        Errore se non ri riescono a trovare le recensioni altrimenti None
    """
    def showAllReview(self, driver):
        # Mostro tutte le recensioni
        try:
            buttonSeeAll = driver.find_element(By.XPATH, '//a[@data-hook="see-all-reviews-link-foot"]')
            buttonSeeAll.click()

            return None
        except:
            return [{
                "error": True,
                "errorDescription": "Nessuna recensione trovata"
            }]


    """Ordina le recensioni
    
    Parametri
    ----------
    driver : seleniumDriver
        Scheda di chrome in cui navigare
    
    Returns
    -------
    """
    def orderReview(self, driver):
        # Ordino le recensione in base a quelle più recenti
        select = wait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//select[@id="sort-order-dropdown"]/option[@value="recent"]')))

        select.click()


    """Ottiene il container principale che contiene tutte le recensioni cosiì da velocizzare le operazioni future
    
    Parametri
    ----------
    driver : seleniumDriver
        Scheda di chrome in cui navigare
    
    Returns
    -------
    seleniumElement
        Contenitore principale
    """
    def readMainContainer(self, driver):
        container = wait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="a-fixed-right-grid view-point"]')))

        return container


    """Ottiene tutte le recensioni presenti nel contenitore principale
    
    Parametri
    ----------
    page: seleniumElement
        Pagina in cui cercare le recensioni
    
    Returns
    -------
    list
        Lista di recensioni
    """
    def readReviews(self, page):
        reviews = page.find_elements(By.XPATH, './/div[@data-hook="review"]')

        return reviews


    """Ottiene il testo contenuto in una recensione
    
    Parametri
    ----------
    review: seleniumElement
        Recensione in cui cercare il testo
    
    Returns
    -------
    string
        Testo della recensione
    """
    def getReviewText(self, review):
        try:
            text = review.find_element(By.XPATH, './/a[@data-hook="review-title"]/span').get_attribute(
                "innerHTML")
        except:
            text = review.find_element(By.XPATH, './/span[@data-hook="review-title"]/span').get_attribute(
                "innerHTML")

        try:
            text += " " + review.find_element(By.XPATH, './/span[@data-hook="review-body"]/span').get_attribute(
                "innerHTML")
        except:
            # Puo non esserci un body della recensione
            text = ""

        return text


    """Apre la prossima pagina che contiene le recensioni
    
    Parametri
    ----------
    page: seleniumElement
        Pagina in cui trovare il link della successiva
    
    Returns
    -------
    boolean
        Se è stata trovata la pagina ritorna True altriemnti False
    """
    def getNextReviewPage(self, page):
        try:
            buttonNext = wait(page, 20).until(EC.element_to_be_clickable((By.XPATH, '//li[@class="a-last"]/a')))

            buttonNext.click()

            result = True
        except:
            # NON CI SONO PIU PAGINE DA ANALIZZARE
            result = False

        return result



"""
    Aggiunge alla string passata come parametro, il contenuto di tutti i tag presenti nella lista itemsFind
    """
def appendTextDetails(itemsFind, text):
    for item in itemsFind:
        text += "-" + item.text

    return text





