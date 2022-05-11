from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import NaiveBayesClassifier
import pickle

import re, string

#Crea i tag ed elimina le parole con il tag che non sono necessarie
def remove_noise(tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tokens):
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

def tokenize(text):
    tokens = word_tokenize(text)
    return tokens

def get_review_for_model(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tokens)

if __name__ == "__main__":

    posFile = open("files/positive.txt", "r")
    negFile = open("files/negative.txt", "r")

    positive = posFile.readlines()
    negative = negFile.readlines()
    #text = twitter_samples.strings('tweets.20150430-223406.json')
    #tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]

    stop_words = stopwords.words('english')

    positive_tokens = []
    negative_tokens = []

    #Tokenizzo le recensioni del dataset
    for el in positive:
        positive_tokens.append(tokenize(el))

    for el in negative:
        negative_tokens.append(tokenize(el))


    #Vengono rimosse le parti non necessarie del testo e viene normalizzato (LEMMATIZE)
    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    positive_tokens_for_model = get_review_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_review_for_model(negative_cleaned_tokens_list)

    positive_dataset = [(review_dict, "Positive")
                         for review_dict in positive_tokens_for_model]

    negative_dataset = [(review_dict, "Negative")
                         for review_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset

    #random.shuffle(dataset)

    #train_data = dataset[:600]
    #test_data = dataset[600:]

    classifier = NaiveBayesClassifier.train(dataset)

    f = open("BayesClassifier_Review.pickle", "wb")
    pickle.dump(classifier, f)
    f.close()

    #print("Accuracy is:", classify.accuracy(classifier, dataset))

    #print(classifier.show_most_informative_features(10))

    """custom_tweet = "I ordered just once from TerribleCo, they screwed up, never used the app again."

    custom_tokens = remove_noise(word_tokenize(custom_tweet))

    print(custom_tweet, classifier.classify(dict([token, True] for token in custom_tokens)))"""