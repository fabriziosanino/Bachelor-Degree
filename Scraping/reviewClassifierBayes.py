from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from nltk.stem import WordNetLemmatizer
import nltk
import pickle
import time
import re, string
import amazonModule

AmazonModule = amazonModule.AmazonModule()

#Crea i tag ed elimina le parole con il tag che non sono necessarie
def remove_noise(tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in nltk.pos_tag(tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


def classify(link, mainDriver):
    mainDriver.get(link)

    mainDriver.implicitly_wait(1)

    # Mostro tutte le recensioni
    """try:
        buttonSeeAll = mainDriver.find_element(By.XPATH, '//a[@data-hook="see-all-reviews-link-foot"]')
        buttonSeeAll.click()
    except:
        return [{
            "error": True,
            "errorDescription": "Nessuna recensione trovata"
        }]"""
    find = AmazonModule.showAllReview(mainDriver)
    if find is not None:
        return find

    #Ordino le recensione in base a quelle più recenti
    """select = wait(mainDriver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//select[@id="sort-order-dropdown"]/option[@value="recent"]')))

    select.click()"""
    AmazonModule.orderReview(mainDriver)

    #Leggo il contenuto del div principale in modo da velocizzare le operazioni di ricerca
    #page = wait(mainDriver, 30).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="a-fixed-right-grid view-point"]')))
    page = AmazonModule.readMainContainer(mainDriver)

    time.sleep(5)

    reviewsText = []

    #Il ciclo si ferma quando sono finite le recensioni (ovvero non viene trovato il bottone) oppure quando trovo 50 recensioni
    while len(reviewsText) < 50:
        #Leggo le recensioni
        #reviews = page.find_elements(By.XPATH, './/div[@data-hook="review"]')
        reviews = AmazonModule.readReviews(page)

        for review in reviews:
            #Estraggo il testo di ciascuna recensione
            """try:
                text = review.find_element(By.XPATH, './/a[@data-hook="review-title"]/span').get_attribute(
                    "innerHTML")
            except:
                text = review.find_element(By.XPATH, './/span[@data-hook="review-title"]/span').get_attribute(
                    "innerHTML")

            try:
                text += " " + review.find_element(By.XPATH, './/span[@data-hook="review-body"]/span').get_attribute(
                    "innerHTML")
            except:
                #Puo non esserci un body della recensione
                None"""
            text = AmazonModule.getReviewText(review)

            reviewsText.append(text)

        #Scelgo la pagina successiva
        """try:
            buttonNext = wait(page, 20).until(EC.element_to_be_clickable((By.XPATH, '//li[@class="a-last"]/a')))

            buttonNext.click()
        except:
            #NON CI SONO PIU PAGINE DA ANALIZZARE
            break"""
        find = AmazonModule.getNextReviewPage(page)
        if not find:
            break

        """page = wait(mainDriver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@class="a-fixed-right-grid view-point"]')))"""
        page = AmazonModule.readMainContainer(mainDriver)

        time.sleep(5)

        print(len(reviewsText))

    f = open("BayesClassifier_Review.pickle", "rb")
    classifier = pickle.load(f)
    f.close()

    numPositive = 0
    numNegative = 0
    numNeutral = 0

    for review in reviewsText:
        tokens = remove_noise(nltk.word_tokenize(review))

        reviewType = classifier.classify(dict([token, True] for token in tokens))

        if reviewType == 'Positive':
            numPositive += 1
        elif reviewType == 'Negative':
            numNegative += 1
        else:
            numNeutral += 1


    return [{
        "error": False,
        "positive": numPositive,
        "negative": numNegative,
        "neutral": numNeutral
    }]