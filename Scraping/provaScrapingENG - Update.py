from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

import reviewClassifierBayes

import mysql.connector
from mysql.connector import Error

from flask import Flask
from flask import request
from flask import jsonify

from concurrent.futures import ThreadPoolExecutor

from itertools import permutations
from itertools import combinations

import json

app = Flask(__name__)

mainDriver = None
drivers = []

s = 'C:/Users/fabri/Desktop/Fabry/3 Uni/2 Semestre/Stage/Scraping/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('--headless')

THREAD_NUMBER = 2  # Numero di thread utilizzati dal server per fare le ricerche nelle descrizioni dei prodotti
FAST_RETRASMIT_ITEM = 5  # Numero che indica quando il server deve inviare i risultati al client. Utilizzato per dare al client risultati in meno
# tempo

""" 
    CONTROLLO NEL TESTO DEL PRODOTTO SE PRESENTI DELLE CARATTERISTICHE INSERITE DALL'UTENTE. VENGONO CONTROLLATE TUTTE LE PERMUTAZIONI DEL TESTO
    INSERITO. SE RIMANGONO DELLE CARATTERISTICHE DA TROVARE SI ANALIZZA LA DESCRIZIONE DEL PRODOTTO, SEMPRE ANDANDO AD UTILIZZARE LE 
    PERMUTAZIONI. SE RIMANGONO ANCORA DELLE CARATTERISTICHE SI CERCANO SE NON PRESENTI LE SINGOLE PAROLE (NATURALEMENTE NON E' QUINDI DETTO
    CHE IL PRODOTTO SIA AFFINE AL 100%) 
"""

# TODO: CERCARE ANCHE NELLE PAGINE SUCCESSIVE

"""
Funzione che cerca nel testo, passato come parametro, tutte le combinazioni possibili di ciascuna caratteristica del prodotto inserite dall'utente.
Ritorna la lista delle caratteristiche che ancora non sono state trovate
"""


def findInProduct(keyName, textToSearch):
    # TODO: aggiungere che le parole possono anche essere attaccate senza spazi
    ausKeyName = keyName.copy()
    for i in range(len(keyName)):
        keyPart = keyName[i].split(' ')
        perms = list(permutations(keyPart))
        for perm in perms:
            if ' '.join(perm) in textToSearch.lower():
                ausKeyName.remove(keyName[i])
                break

    # Provo tutte le combinazioni, nell'ordine in cui l'utente ha scritto
    """
    ES. 16 gb ram -> combinazioni = 16 gbram, gb 16ram, ram 16gb, 16gb ram, 16ram gb, gbram 16
    """
    keyName = ausKeyName.copy()
    for i in range(len(keyName)):
        keyPart = keyName[i].split(' ')
        listCombinations = list()

        for n in range(1, len(keyPart)):
            listCombinations += list(combinations(keyPart, n))

        for combination in listCombinations:
            remainingPart = list(set(keyPart) - set(combination))

            stringToFind = ''.join(combination) + " " + ''.join(remainingPart)
            if stringToFind in textToSearch.lower():
                ausKeyName.remove(keyName[i])
                break

    return ausKeyName


"""
Aggiunge alla string passata come parametro, il contenuto di tutti i tag presenti nella lista itemsFind
"""

def appendTextDetails(itemsFind, text):
    for item in itemsFind:
        text += "-" + item.text

    return text


"""
Funzione che analizza ciascun prodotto. Analizza il nome e se e solo se necessario i dettagli.
Per analizzare i dettagli utilizza un instanza del browser creata inizialmente dal main in modo da fare più veloce
"""


def inspectProduct(item, keyList, pos):
    totalWord = 0
    for key in keyList:
        totalWord += len(key.split(' '))

    totalLetter = 0
    for element in keyList:
        totalLetter += len(element)

    productName = ""
    try:
        productName = item.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')
    except:
        # ALCUNI PRODOTTI COPRONO UNA RIGA INTERA
        productName = item.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]')

    try:
        productPrice = item.find_element(By.XPATH, './/span[@class="a-offscreen"]').get_attribute("innerHTML")
    except:
        productPrice = ""

    print(productName.get_attribute("innerHTML"))

    # Controlla che siano presenti nel nome tutte le parole chiave inserite dall'utente
    """findAll = True
    for key in keyListName:
        if key.lower() not in productName.get_attribute("innerHTML").lower():
            findAll = False
            break"""

    previousLengthOfKeyList = len(keyList)

    textToSearch = productName.get_attribute("innerHTML").lower()

    keyList = findInProduct(keyList, textToSearch)

    linkProduct = item.find_element(By.XPATH,
                                    './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')

    if len(keyList) == 0:
        # Sono state trovate tutte le caratteristiche
        imageProduct = item.find_element(By.XPATH, './/img[@class="s-image"]')

        return {"name": productName.get_attribute("innerHTML").lower(),
                "productLink": linkProduct.get_attribute("href"),
                "productImage": imageProduct.get_attribute("src"),
                "productPrice": productPrice,
                "reliability": 100}
    # elif len(keyList) == previousLengthOfKeyList:
    # E' molto difficile che sia un prodotto target perchè nel nome non c'è nemmeno una key
    # return {}
    else:
        # Utilizzo l'instanza di google chrome per cercare il prodotto
        drivers[pos].get(linkProduct.get_attribute("href"))
        drivers[pos].implicitly_wait(0.5)

        externalContainer = wait(drivers[pos], 10).until(
            EC.presence_of_all_elements_located((By.ID, 'featurebullets_feature_div')))
        infos = externalContainer[0].find_elements(By.XPATH, './/span[@class="a-list-item"]')

        # Metto in una stringa comune tutte le descrizioni in modo da fare la ricerca in modo più veloce
        textToSearch = appendTextDetails(infos, textToSearch)
        # for info in infos:
        # text = info.text
        # textToSearch += "-" + text
        try:
            descriptions = wait(drivers[pos], 10).until(
                EC.presence_of_all_elements_located((By.ID, 'productDescription')))
            p = descriptions[0].find_element(By.TAG_NAME, 'p')  # TODO: CONTROLLARE SE POSSONO ESSERE PRESENTI PIU P
            textToSearch += "-" + p.text
        except:
            # ALCUNI PRODOTTI NON HANNO LA DESCRIZIONE
            None
        finally:
            # Controllo se sono presenti tutte le caratteristiche richieste

            try:
                detailsTable = wait(drivers[pos], 10).until(
                    EC.presence_of_all_elements_located((By.ID, 'productDetails_techSpec_section_1')))
                details = detailsTable[0].find_elements(By.XPATH, './/td["a-size-base prodDetAttrValue"]')

                textToSearch = appendTextDetails(details, textToSearch)
            except:
                # ALCUNI PRODOTTI NON HANNO LA TABELLA DEI DETTAGLI
                None
            finally:
                keyListName = findInProduct(keyList, textToSearch)

                if len(keyListName) == 0:
                    imageProduct = item.find_element(By.XPATH, './/img[@class="s-image"]')

                    return {"name": productName.get_attribute("innerHTML").lower(),
                            "productLink": linkProduct.get_attribute("href"),
                            "productImage": imageProduct.get_attribute("src"),
                            "productPrice": productPrice,
                            "reliability": 100}
                else:
                    # Ultima prova cercando le parole rimananeti senza che esse siano collegate ma basta che siano presenti nel testo
                    findAll = True
                    for key in keyList:
                        for splitted in key.split(' '):
                            if not any(splitted in word for word in
                                       textToSearch.lower().split(' ')):  # Divide le key in singole parole
                                findAll = False
                                break

                        if not findAll:
                            break

                    if findAll:
                        imageProduct = item.find_element(By.XPATH, './/img[@class="s-image"]')

                        # Conta il numero di parole che non sono state trovate
                        wordNotFoundInOrderCount = 0
                        for key in keyList:
                            wordNotFoundInOrderCount += len(key.split(' '))

                        countLetter = 0
                        for key in keyList:
                            countLetter += len(key)

                        firstCalculation = (90 * totalWord) / wordNotFoundInOrderCount
                        secondCalculation = (90 * totalLetter) / countLetter

                        reliability = 100 - ((firstCalculation + secondCalculation) / 2)
                        if reliability <= 0:
                            reliability = 5

                        return {"name": productName.get_attribute("innerHTML").lower(),
                                "productLink": linkProduct.get_attribute("href"),
                                "productImage": imageProduct.get_attribute("src"),
                                "productPrice": productPrice,
                                "reliability": reliability}
                    else:
                        return {}


"""
Servlet che elimina una ricerca salvata
"""

@app.route("/deleteResearch", methods=['POST'])
def deleteResearch():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=UTF-8':
        return {"error": "Content-Type not supported!"}, 422
    else:
        clientParameter = json.loads(request.get_data(), strict=False)
        idResearch = clientParameter["idResearch"]

        try:
            connection = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='savedResearch')

            if connection.is_connected():
                cursor = connection.cursor()

                try:
                    #Elimino tutti i prodotti della ricerca
                    cursor.execute("DELETE FROM savedproducts WHERE researchNum = " + str(idResearch))

                    connection.commit()

                    #Elimino la ricerca
                    cursor.execute("DELETE FROM search WHERE id = " + str(idResearch))

                    connection.commit()

                    connection.close()

                    return jsonify([{
                        "error":False
                    }])
                except:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

                    return jsonify([{
                        "error": True,
                        "errorDescription": "Error while deleting"
                    }])
        except:
            return jsonify([{
                "error": True,
                "errorDescription": "Connection error"
            }])



"""
Servlet per ottenere i dettagli di una ricerca (i prodotti di quella ricerca)
"""

@app.route("/getResearchDetail", methods=['POST'])
def getResearchDetail():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=UTF-8':
        return {"error": "Content-Type not supported!"}, 422
    else:
        clientParameter = json.loads(request.get_data(), strict=False)
        idResearch = clientParameter["idResearch"]

        try:
            connection = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='savedResearch')

            if connection.is_connected():
                cursor = connection.cursor()

                try:
                    cursor.execute("SELECT * FROM savedproducts WHERE researchNum = " + str(idResearch))

                    results = cursor.fetchall()

                    returnValue = [{
                        "error": False
                    }]

                    for row in results:
                        returnValue.append({
                            "productName": row[1],
                            "productLink": row[2],
                            "productImg": row[3],
                            "reliability": row[4],
                            "price": row[5]
                        })

                    connection.close()

                    return jsonify(returnValue)
                except:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

                    return jsonify([{
                        "error": True,
                        "errorDescription": "Error while finding products"
                    }])
        except:
            return jsonify([{
                "error": True,
                "errorDescription": "Connection error"
            }])


"""
Servlet che restituisce tutte le ricerche effettuate
"""

@app.route("/readResearches", methods=['POST'])
def readResearches():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=UTF-8':
        return {"error": "Content-Type not supported!"}, 422
    else:
        try:
            connection = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='savedResearch')

            if connection.is_connected():
                cursor = connection.cursor()

                try:
                    cursor.execute("SELECT * FROM search")

                    results = cursor.fetchall()

                    returnValue = [{
                        "error": False
                    }]

                    for row in results:
                        #Per ogni ricerca, prendo le immagini dei primi 3 prodotti
                        cursor.execute("SELECT productImg FROM savedproducts WHERE researchNum = " + str(row[0]) + " LIMIT 3;")

                        resultImg = cursor.fetchall()

                        el = {
                            "id": row[0],
                            "name": row[1],
                            "numElements": row[2],
                            "images": []
                        }


                        for img in resultImg:
                            el["images"].append(img[0])

                        returnValue.append(el)


                    connection.close()
                    return jsonify(returnValue)
                except:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

                    return jsonify([{
                        "error": True,
                        "errorDescription": "Cannot find saved searches"
                    }])
        except:
            return jsonify([{
                "error": True,
                "errorDescription": "Connection error"
            }])

"""
Servlet che permette di salvare sul DB una ricerca effettuata
"""

@app.route("/saveResearch", methods=['POST'])
def saveResearch():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=UTF-8':
        return {"error": "Content-Type not supported!"}, 422
    else:
        clientParameter = json.loads(request.get_data(), strict=False)
        products = clientParameter["products"]
        nameResearch = clientParameter["nameResearch"]

        try:
            connection = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='savedResearch')

            if connection.is_connected():
                cursor = connection.cursor()

                try:
                    #Inserisco la ricerca
                    cursor.execute("INSERT INTO search VALUES(NULL, '" + nameResearch + "', " + str(len(products)) + ")")

                    connection.commit()

                    idResearchInserted = cursor.lastrowid

                    try:
                        #Inserisco tutti i prodotti con il riferimento alla ricerca
                        for product in products:
                            query = "INSERT INTO savedproducts VALUES(NULL, '" + str(product["productName"]) + "', '" + str(product["productLink"]) + "', '" + str(product["productImg"]) + "', '" + str(product["reliability"]) + "', '" + str(product["price"]) + "', " + str(idResearchInserted) + ")"
                            cursor.execute(query)

                            connection.commit()

                        connection.close()

                        return jsonify([{
                            "error": False
                        }])
                    except:
                        if connection.is_connected():
                            cursor.close()
                            connection.close()

                        return jsonify([{
                            "error": True,
                            "errorDescription": "Unable to save products"
                        }])
                except:
                    #C'è una ricerca già con quel nome (il campo nome è UNIQUE sul DB)
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

                    return jsonify([{
                        "error": True,
                        "errorDescription": "The search has already been saved"
                    }])
        except:
            return jsonify([{
                "error": True,
                "errorDescription": "Connection error"
            }])

"""
    Servlet che classifica un prodotto in base alle recensioni
"""


@app.route("/classifyReview", methods=['POST'])
def classifyReview():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=UTF-8':
        return {"error": "Content-Type not supported!"}, 422
    else:
        clientParameter = request.get_json()
        result = reviewClassifierBayes.classify(clientParameter["link"], mainDriver)

        return jsonify(result)


"""
Servelt che riceve come parametri 'keywordProductName' cioè il nome del prodotto, 'startIndexResearch' che è l'indice da cui 
partire nella ricerca degli elementi e 'firstRequest' che indica al server se è la prima ricerca di filtraggio di quell'elemento. 
Siccome ogni FAST_RETRASMIT_ITEMS si inviano i risultati al client al passo successivo non si deve ricominciare dall'inzio 
ma bisogna partire da dove si era finito in precedenza usando 'startIndexResearch'. 
Questa servlet cerca in una pagina amazon il nome del prodotto, dopo di che crea THRED_NUMBER thread che definiscono se è un prodotto target 
oppure no. 
"""


@app.route("/getProducts", methods=['POST'])
def getProducts():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=UTF-8':
        return {"error": "Content-Type not supported!"}, 422
    else:
        clientParameter = request.get_json()
        keywordProductName = clientParameter["keywordName"]
        keyListProductName = keywordProductName.split(',')

        findMore = clientParameter["findMore"]

        # keywordProductCharateristics = clientParameter["keywordCharateristics"]
        # keyListProductCharateristics = keywordProductCharateristics.split(' ')

        """if keywordProductCharateristics != "":
            findDetails = True
        else:
            findDetails = False"""

        startIndexResearch = int(clientParameter["startIndex"])

        firstRequest = bool(clientParameter["firstRequest"])

        # TODO: deleteConnectors(keyList)

        resultItems = []

        # Navigo sulla pagina di amazon e cerco il nome del prodotto. Se findMore è true, ho già i prodotti
        linkAmazon = 'https://www.amazon.com'

        if firstRequest:
            mainDriver.get(linkAmazon)

            mainDriver.implicitly_wait(1)
            search = mainDriver.find_element(By.ID, 'twotabsearchtextbox')
            search.send_keys(keywordProductName.replace(',', ' '))
            search.send_keys(Keys.ENTER)

            mainDriver.implicitly_wait(0.5)
        elif findMore:
            linkNextPage = clientParameter["linkNextPage"]
            mainDriver.get(linkNextPage)

            mainDriver.implicitly_wait(1)
        else:
            linkRemainingProducts = clientParameter["linkRemainingProducts"]
            mainDriver.get(linkRemainingProducts)

            mainDriver.implicitly_wait(1)

        # Ottengo tutti i prodotti in base alla classe che hanno nell'html
        items = wait(mainDriver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@data-component-type, "s-search-result")]')))

        startItemsNumber = len(items)

        # Creo un pool di thread
        executor = ThreadPoolExecutor(THREAD_NUMBER)

        fastTrasmit = False

        # Elimino tutti gli elementi che ho già eventualemente analizzato nelle precedenti ricerche
        del items[0:startIndexResearch]

        numOfItems = len(items)

        # Intestazione del json da restituire al client
        resultItems.append({
            "itemsNum": 0,  # PRODOTTI CHE SONO STATI ANALIZZATI
            "fastRetrasmitPosition": 0,
            # LA POSIZIONE INDICA L'ITEM DELLA PAGINA AMAZON A CUI IL PROGRAMMA è ARRIVATO ANALIZZANDO
            "errors": False,  # SE E' TRUE SIGNIFICA CHE CI SONO STATI DEGLI ERRORI
            "firstRequest": firstRequest,
            # INDICA SE IL CLIENT E' LA PRIMA RICHIESTA CHE FA PER QUEL DETERMINATO FILTRO
            "stillElementsToAnalyze": False,  # INDICA AL CLIENT SE CI SONO ANCORA ELEMENTI DA ANALIZZARE OPPURE NO
            "linkNextPage": "",
            "linkRemainingProducts": "",
            "findMore": findMore
        })

        if numOfItems != 0:
            numOfThread = THREAD_NUMBER

            numOfCycle = (numOfItems // THREAD_NUMBER)  # numero di volte che è necessario utilizzare i thread
            if numOfItems % THREAD_NUMBER != 0:
                numOfCycle += 1  # il numero di item non è un multiplo del numero di thread

            notMultiple = False

            # Devo usare i thred in base a quanti sono i thread e in base a quanti sono gli items
            for i in range(numOfCycle):
                if i == len(
                        items) // THREAD_NUMBER:  # Siamo arrivati all'ultimo range di elementi che non è multiplo del numero di thread
                    numOfThread = numOfItems
                    notMultiple = True

                threads = []
                for j in range(0, numOfThread):
                    # future = executor.submit(inspectProduct, items[(THREAD_NUMBER * i) + j], keyListProductName, keyListProductCharateristics, findDetails, j, )
                    future = executor.submit(inspectProduct, items[(THREAD_NUMBER * i) + j], keyListProductName.copy(),
                                             j, )
                    threads.append(future)

                # Aspetto i risultati di ciascun thread
                for x in threads:
                    res = x.result()
                    if res != {}:
                        resultItems.append(res)
                if notMultiple:
                    numOfItems = 0
                else:
                    numOfItems -= THREAD_NUMBER

                if (len(resultItems) - 1) >= FAST_RETRASMIT_ITEM:  # -1 PERCHE' C'E' L'HEADER INIZIALE
                    fastTrasmit = True  # INVIO I PRIMI FAST_RESTRASMIT_ITEM RISULTATI IN MODO DA NON FAR ATTENDERE TROPPO L'UTENTE...
                    break

            if fastTrasmit and numOfItems > 0:
                resultItems[0]["stillElementsToAnalyze"] = True
                resultItems[0]["itemsNum"] = len(items) - numOfItems
                resultItems[0]["fastRetrasmitPosition"] = int(startItemsNumber) - int(
                    numOfItems)  # POSIZIONE IN CUI E' ARRIVATO AD ANALIZZARE
                resultItems[0]["linkRemainingProducts"] = mainDriver.current_url
            else:
                #TODO: controllare se fiinisce sempre
                #Non ci sono più elementi da analizzare
                resultItems[0]["itemsNum"] = len(items)

                linkNextPage = wait(mainDriver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//span[@class="s-pagination-strip"]/a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]')))
                linkNextPage = linkNextPage[0].get_attribute("href")
                resultItems[0]["linkNextPage"] = linkNextPage
        else:
            if firstRequest:
                resultItems[0]["errors"] = True

        return jsonify(resultItems)


# DOVREBBE ESSERE FATTO PER OGNI RICHIESTA
"""
Apre THREAD_NUMBER pagine di google chrome in modo che possono essere fatte le ricerche tramite selenium
"""


def startDrivers():
    for i in range(THREAD_NUMBER):
        global drivers
        driver = webdriver.Chrome(options=options, executable_path=s)
        drivers.append(driver)


"""
Apre 1 pagina di google chrome in cui si farà la ricerca iniziale con il nome del prodotto
"""


# DOVREBBE ESSERE FATTO PER OGNI RICHIESTA
def startMainDriver():
    global mainDriver
    mainDriver = webdriver.Chrome(options=options, executable_path=s)


"""
Apre le varie pagine di google chrome e avvia il server
"""
if __name__ == "__main__":
    startDrivers()
    startMainDriver()

    app.run(debug=True)
