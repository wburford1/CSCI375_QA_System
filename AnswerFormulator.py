# Nevin Bernet

import nltk
from nltk import ne_chunk
from nltk import pos_tag
from nltk import word_tokenize
from QuestionProcessor import QuestionProcessor
from PassageRetriever import PassageRetriever


# A class for formatting answers given a question
class AnswerFormulator:

    def __init__(self):
        self.question = None
        self.passages = None

    # question is a QuestionProcessor object, passages is a PassageRetriever object with 'question' set at the question
    def set_question(self, question, passages):

        self.clear()
        self.question = question
        self.passages = passages

    # clears the AnswerFormatter object so that it can be used with another question
    def clear(self):

        self.question = None
        self.passages = None

    # Returns the question type, ussually specified by its 'W' word, ie 'who is that' would return 'who'
    def get_questiontype(self):

        return 'W'

    # Returns the kind of answer that the question implies. ie 'where' questions would return location, who questions would return person
    def get_answertype(self):

        qt = self.get_questiontype()

        if qt == 'WHO':
            return 'PERSON/ORG'
        elif qt == 'WHERE':
            return 'PLACE'
        elif qt == 'WHEN':
            return 'DATE/TIME'
        elif qt == 'WHAT':
            return 'NOUNPHRASE'
        elif qt == 'WHICH':
            return 'ELEMENTOF'
        elif qt == 'WHY':
            return 'JUSTIFICATION'
        elif qt == 'HOW':
            return 'DESCRIPTION'

    # returns an array of ten answers where [0] is the 'best' answer and [9] is the tenth best
    # question and passages must not be equal to None
    def get_answers(self):

        at = self.get_answertype()
        print(named_entities)

        if at == 'WHO' or at == 'WHERE' or at == 'WHEN':
            print('')


# testing
if __name__ == '__main__':

    if False:
        print('false')

    if True:
        qp = QuestionProcessor('What hockey team did Wayne Gretzky play for?')
        pr = PassageRetriever()
        pr.set_question(0, qp.get_keywords(), 'train', 20)
        af = AnswerFormulator()
        af.set_question(qp, pr)
        af.get_answers()
