# Nevin Bernet

from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.chunk import tree2conlltags
from QuestionProcessor import QuestionProcessor
from PassageRetriever import PassageRetriever


# A class for formatting answers given a question
class AnswerFormulator:
    question_types = 'WHO', 'WHAT', 'WHERE', 'WHEN', 'WHICH', 'WHY', 'HOW'

    def __init__(self):
        # the question in plain text
        self.question = None
        # a POS tagged version of the question
        self.tokenized_q = None
        # a named entity IOB tagged version of the question
        self.ne_tagged_q = None
        # a list of ScoredPassage objects as defined in PassageRetriever
        self.passage_objs = None

    # question is a string, passages is a list of passage objects defined in PassageRetriever
    def set_question(self, question, passages):
        self.clear()
        self.question = question
        self.tokenized_q = word_tokenize(question)
        self.ne_tagged_q = tree2conlltags(ne_chunk(pos_tag(self.tokenized_q)))
        self.passage_objs = passages

    # clears the AnswerFormatter object so that it can be used with another question
    def clear(self):
        self.question = None
        self.tokenized_q = None
        self.ne_tagged_q = None
        self.passage_objs = None

    # Returns the question type, ussually specified by its 'W' word, ie 'who is that' would return 'who'
    def get_questiontype(self):
        # think about question 20: "Tell me what...". Prob just a what question
        # think about question 91, 93: "Name a ...".
        first_word = self.tokenized_q[0].upper()
        if first_word in AnswerFormulator.question_types:
            return first_word
        if first_word == "WHAT'S":
            return 'WHAT'
        return 'W'

    # Returns the kind of answer that the question implies.
    # ie 'where' questions would return location, who questions would return person
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
    def get_answers(self, count=10):

        at = self.get_answertype()
        print(self.ne_tagged_q)

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
