# HomeworkFive

import nltk
from nltk.corpus import stopwords
import string

# a class for processing questions
class QuestionProcessor:

    #a list of key words from the question
    key_words = []

    #the original question
    question = ''
    
    #constructs a QuestionProcessor object for 'question'
    #q is a question
    def __init__ (self, q):

        global question
        global key_words
        
        question = q
        key_words = []
        
        self.process()

    #tokenizes question, removes stopwords and makes anything in quotations its own token, also removes punctuation. 
    def process(self):

        global key_words
        toks = nltk.word_tokenize(question)

        i = 0
        while i < len(toks):

            quotes = ['``', "''", '"']

            #if there is a quoted entity in the question, it is added in its entirety to the list of key words
            if toks[i] in quotes:
                i+=2
                tok = toks[i-1]
                while not toks[i] in quotes:
                    tok = ' '.join([tok, toks[i]])
                    i+= 1
                i+=1
                key_words.append(tok)
            #if a token is not a stopword, it is added to the list of key words
            else:
                if toks[i] not in set(stopwords.words('english')):
                    key_words.append(toks[i])
                i+=1

        #removes punctuation 
        key_words = [word for word in key_words if not word in list(string.punctuation)]
                        
        print question
        print key_words

    def get_keywords():
        return key_words

    def get_question():
        return question

    def set_question(q):

        clear()
        question = q
        process()

    def clear():
        
        question = ''
        key_words = []
        
'''
testing
if __name__ == '__main__':
    process_question = QuestionProcessor('What is the length, of "tail of two cities"')
'''
