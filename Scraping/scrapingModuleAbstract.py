from abc import ABC, abstractmethod

class AbstractModule(ABC):
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
    @abstractmethod
    def navigateToProducts(self, driver, productName):
        pass


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
    @abstractmethod
    def getProducts(self, driver):
        pass


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
    @abstractmethod
    def getLinkNextPage(self, driver):
        pass


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
    @abstractmethod
    def getProductName(self, item):
        pass


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
    @abstractmethod
    def getProductPrice(self, item):
        pass


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
    @abstractmethod
    def getLinkProduct(self, item):
        pass


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
    @abstractmethod
    def getProductReviewRating(self, item):
        pass


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
    @abstractmethod
    def getLinkProductImg(self, item):
        pass


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
    @abstractmethod
    def getProductDetails(self, driver, linkProduct, textToSearch):
        pass


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
    @abstractmethod
    def showAllReview(self, driver):
        pass


    """Ordina le recensioni

    Parametri
    ----------
    driver : seleniumDriver
        Scheda di chrome in cui navigare

    Returns
    -------
    """
    @abstractmethod
    def orderReview(self, driver):
        pass


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
    @abstractmethod
    def readMainContainer(self, driver):
        pass


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
    @abstractmethod
    def readReviews(self, page):
        pass


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
    @abstractmethod
    def getReviewText(self, review):
        pass


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
        pass