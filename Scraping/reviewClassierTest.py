from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk.corpus
from textblob import TextBlob
import time
import re

import amazonModule

def clean(text):
    text = re.sub('[^A-Za-z]+', ' ', text)
    return text

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    return tokens

def deleteStopWords(text):
    newText = (" ").join(ele for ele in text.split(" ") if ele.lower() not in stopwords.words('english'))
    return newText

def posTag(text):
    pos = nltk.pos_tag(text)
    return pos

pos_dict = {'J':wordnet.ADJ, 'V':wordnet.VERB, 'N':wordnet.NOUN, 'R':wordnet.ADV}
wordnet_lemmatizer = WordNetLemmatizer()
def lemmatize(pos_data):
    lemma_rew = " "
    for word, pos in pos_data:
        pos = pos_dict.get(pos[0]) #trasforma dalla notazione piu lunga alla notazione pos_dict
        if not pos:
            lemma = word
            lemma_rew = lemma_rew + " " + lemma
        else:
            lemma = wordnet_lemmatizer.lemmatize(word, pos=pos)
            lemma_rew = lemma_rew + " " + lemma
    return lemma_rew

# function to calculate subjectivity
def getSubjectivity(review):
    return TextBlob(review).sentiment.subjectivity

# function to calculate polarity
def getPolarity(review):
    return TextBlob(review).sentiment.polarity

# function to analyze the reviews
def analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def classify(link, mainDriver):
    mainDriver.get(link)

    mainDriver.implicitly_wait(1)

    #Mostro tutte le recensioni
    """try:
        buttonSeeAll = mainDriver.find_element(By.XPATH, '//a[@data-hook="see-all-reviews-link-foot"]')
        buttonSeeAll.click()

        #time.sleep(1)
    except:
        return [{
            "error": True,
            "errorDescription": "Nessuna recensione trovata"
        }]"""
    find = amazonModule.showAllReview(mainDriver)
    if find is not None:
        return find

    #Ordino le recensione in base a quelle più recenti
    """select = wait(mainDriver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//select[@id="sort-order-dropdown"]/option[@value="recent"]')))

    select.click()"""
    amazonModule.orderReview(mainDriver)

    #Leggo il contenuto del div principale in modo da velocizzare le operazioni di ricerca
    #page = wait(mainDriver, 30).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="a-fixed-right-grid view-point"]')))
    page = amazonModule.readMainContainer(mainDriver)

    time.sleep(5)

    reviewsText = []

    #Il ciclo si ferma quando sono finite le recensioni (ovvero non viene trovato il bottone) oppure quando trovo 50 recensioni
    while len(reviewsText) < 50:
        #Leggo le recensioni
        #reviews = page.find_elements(By.XPATH, './/div[@data-hook="review"]')
        reviews = amazonModule.readReviews(page)

        for review in reviews:
            #Estraggo il testo di ciascuna recensione
            """try:
                text = review.find_element(By.XPATH, './/a[@data-hook="review-title"]/span').get_attribute(
                    "innerHTML")
            except:
                text = review.find_element(By.XPATH, './/span[@data-hook="review-title"]/span').get_attribute(
                    "innerHTML")

            text += " " + review.find_element(By.XPATH, './/span[@data-hook="review-body"]/span').get_attribute(
                "innerHTML")"""
            text = amazonModule.getReviewText(review)

            reviewsText.append(text)

        #Scelgo la pagina successiva
        """try:
            buttonNext = wait(page, 20).until(EC.element_to_be_clickable((By.XPATH, '//li[@class="a-last"]/a')))

            buttonNext.click()
        except:
            #NON CI SONO PIU PAGINE DA ANALIZZARE
            break"""
        find = amazonModule.getNextReviewPage(page)
        if not find:
            break

        """page = wait(mainDriver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@class="a-fixed-right-grid view-point"]')))"""

        page = amazonModule.readMainContainer(mainDriver)

        time.sleep(5)

        print(len(reviewsText))


    #1. Ripulire il testo con un espressione regolare. Elimina i catatteri speciali e i numeri
    for i in range(len(reviewsText)):
        reviewsText[i] = clean(reviewsText[i])

    #2. Eliminare le stop words. Vengono canellate tutte quelle parole che non sono necessarie per valutare se una frase è positiva o negativa
    for i in range(len(reviewsText)):
        reviewsText[i] = deleteStopWords(reviewsText[i])

    tokensText = []
    #3. Tokenizzare il testo con l'apposita funzione. Il testo viene splittato in parole
    for i in range(len(reviewsText)):
        tokensText.append(tokenize(reviewsText[i]))

    taggedText = []
    #4. Aggiungere per ogni parola un tag. Ad ogni parola viene associato un tag che ne indica il tipo (verbo, nome, ...)
    for i in range(len(reviewsText)):
        taggedText.append(posTag(tokensText[i]))

    #5. Prendo solo le parole che sono interessanti (lemmitize). Cattura solo le parole che hanno i tag necessari per la classificazione
    for i in range(len(taggedText)):
        taggedText[i] = lemmatize(taggedText[i])

    numPositive = 0
    numNegative = 0
    numNeutral = 0

    #6. Classifico il prodotto. In base alle parole rimaste della recensione essa viene classificata
    for i in range(len(taggedText)):
        polarity = getPolarity(taggedText[i])
        if analysis(polarity) == 'Positive':
            numPositive += 1
        elif analysis(polarity) == 'Negative':
            numNegative += 1
        else:
            numNeutral += 1

    return [{
        "error": False,
        "positive": numPositive,
        "negative": numNegative,
        "neutral": numNeutral
    }]