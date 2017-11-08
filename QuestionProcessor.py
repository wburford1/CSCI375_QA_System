# HomeworkFive

import nltk
from nltk.corpus import stopwords
import string


# a class for processing questions
class QuestionProcessor:
    # constructs a QuestionProcessor object for 'question'
    # q is a question
    def __init__(self):

        self.question = None
        self.key_words = []
        self.stop_words = []

    # tokenizes question, removes stopwords and makes anything in quotations its own token, also removes punctuation.
    def process(self):
        toks = nltk.word_tokenize(self.question)

        i = 0
        while i < len(toks):

            quotes = ['``', "''", '"']

            # if there is a quoted entity in the question, it is added in its entirety to the list of key words
            if toks[i] in quotes:
                i += 2
                tok = toks[i-1]
                while not toks[i] in quotes:
                    tok = ' '.join([tok, toks[i]])
                    i += 1
                i += 1
                self.key_words.append(tok.lower())
            # if a token is not a stopword, it is added to the list of key words
            else:
                if toks[i] not in set(stopwords.words('english')):
                    self.key_words.append(toks[i].lower())
                else:
                    self.stop_words.append(toks[i].lower())
                i += 1

        # removes punctuation
        self.key_words = [word for word in self.key_words if word not in list(string.punctuation)]

        # print(self.question)
        # print(self.key_words)

    def get_keywords(self):
        return self.key_words

    def get_question(self):
        return self.question

    def get_stopwords(self):
        return self.stop_words

    def set_question(self, q):
        self.clear()
        self.question = q
        self.process()

    def clear(self):
        self.question = None
        self.key_words = []

    def find_keywords(self, q):
        self.set_question(q)
        return self.key_words


# testing
if __name__ == '__main__':
    process_question = QuestionProcessor('What is the length, of "tail of two cities"')
    process_question.set_question('What team did Wayne Gretzky play for?')
