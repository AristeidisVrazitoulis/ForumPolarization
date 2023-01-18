from flair.models import TextClassifier
from flair.data import Sentence
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentClassifier():
    def __init__(self):
        #self.flair_classifier = TextClassifier.load('en-sentiment')
        self.vader_classifer = SentimentIntensityAnalyzer()


    def flair_classify(self, text):
        sentence = Sentence(text)
        self.flair_classifier.predict(sentence)
        score = sentence.labels[0]
        if "POSITIVE" in str(score):
            return 1
        elif "NEGATIVE" in str(score):
            return -1
        else:
            return 0


    def vader_classify(self, text):
        sentiment_dict = self.vader_classifer.polarity_scores(text)
        if sentiment_dict['compound'] >= 0.05 :
            return 1
        elif sentiment_dict['compound'] <= - 0.05 :
            return -1
        else :
            return 0





if __name__ == "__main__":
    classifier = SentimentClassifier()
    print(classifier.vader_classify("THis is definetely the best cream in the town"))
    print(classifier.vader_classify("Bob is so desperate..."))
    print(classifier.vader_classify("The weather is amazing in Ioannina"))
    print(classifier.vader_classify("What about pita gyros?"))
    print(classifier.vader_classify("It was very good with the price of a stomach ache"))

