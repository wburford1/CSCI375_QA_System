# Nevin Bernet

import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.chunk import tree2conlltags
from nltk.corpus import stopwords
from QuestionProcessor import QuestionProcessor
from PassageRetriever import PassageRetriever
import re
import collections

# A class for formatting answers given a question
class AnswerFormulator:
    question_types = 'WHO', 'WHAT', 'WHERE', 'WHEN', 'WHICH', 'WHY', 'HOW', 'NAME', 'CAN'

    def __init__(self):
        # the question in plain text
        self.question = None
        # a POS tagged version of the question
        self.tokenized_q = None
        # a named entity IOB tagged version of the question
        self.ne_tagged_q = None
        # a list of ScoredPassage objects as defined in PassageRetriever
        self.passage_objs = None
        self.tokenized_passages = None

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
        self.tokenized_passages = None

    # Returns the question type, ussually specified by its 'W' word, ie 'who is that' would return 'who'
    def get_questiontype(self):
        # think about question 20: "Tell me what...". Prob just a what question
        # think about question 91, 93: "Name a ...".

        for word in self.tokenized_q:
            if word.upper() in AnswerFormulator.question_types:
                q_word = word.upper()
                break

        return q_word

    # Returns the kind of answer that the question implies.
    # ie 'where' questions would return location, who questions would return person
    def get_answertype(self):

        qt = self.get_questiontype()

        if qt == 'WHO':
            return ['PERSON', 'ORGANIZATION']
        elif qt == 'WHERE':
            return ['LOCATION', 'GPE', 'FACILITY']
        elif qt == 'WHEN':
            return ['TIME', 'DATE']
        elif qt == 'NAME':
            return ['ORGANIZATION', 'PERSON', 'LOCATION', 'DATE', 'TIME', 'MONEY', 'PERCENT', 'FACILITY', 'GPE']
        elif qt == 'WHAT':
            return ['NOUNPHRASE']
        elif qt == 'WHICH':
            return ['ELEMENTOF']
        elif qt == 'WHY':
            return ['JUSTIFICATION']
        elif qt == 'HOW':
            return ['DESCRIPTION']

    # returns an array of ten answers where [0] is the 'best' answer and [9] is the tenth best
    # question and passages must not be equal to None
    def get_answers(self, count=10):

        possible_answers = {}
        at = self.get_answertype()
        stopword_set = set(stopwords.words('english'))

        #a list of tokenized, relevant passages with all the stopwords removed
        not_stopwords_passages = [[e for e in element.passage if e not in stopword_set] for element in self.passage_objs]
        ne_passages = [[e for e in tree2conlltags(ne_chunk(pos_tag(element.passage))) if not e[2] == 'O'] for element in self.passage_objs]
        ne_passages = [e for e in ne_passages if not len(e) == 0]
        
        if self.get_questiontype() in ['WHO', 'WHERE', 'WHEN', 'NAME']:
            #goes through every named entity in the passages and if a given named entity's type is in at then it adds that answer to possible answers or increments that answer's score by 1 if it already exists in possible aswers
            for passage in ne_passages:
                for e in passage:
                    if e[2][e[2].index('-') + 1:] in at and e[0] not in word_tokenize(self.question):
                        if e[0] not in possible_answers:
                            possible_answers[e[0]] = 1
                        else:
                            possible_answers[e[0]] += 1

        elif self.get_answertype() == 'DEF':
            possible_answers = self.satisfies_patterns('DEF')
            
        return self.ordered_answers([], possible_answers, count)

    #A method for finding finding patterns in the passages
    #returns a dictionary of Strings found in the passages linked to the confidence in each String, where each String satisfies a pattern corresponding to 'pattern_type'
    def satisfies_patterns(self, pattern_type):

        #passages_as_string = 
        
        if pattern_type == 'DEF':
            def_patterns = ['<SUBJECT> is a .+\.', '[,.].+ such as <SUBJECT>', '<SUBJECT> are .+.', '<SUBJECT>, .+,']
            for pattern in self.pattern_objs
                
        

    #recursive method for ordering answers 1-count given a number of possible answers
    #'possibilities' is a dictionary of answer:confidence where confidence is a quantified measure of increasing confidence in the answer
    #returns a list of answers in order from best to worst of length count OR the max possible length given the number of possible answers
    def ordered_answers(self, answers, possibles, count=10):
        if len(answers) == count or len(possibles) == 0:
            return answers
        else:
            greatest = list(possibles)[0]
            for pos in possibles:
                if possibles[pos] > possibles[greatest]:
                    greatest = pos
            del possibles[greatest]
            answers.append(greatest)
            return self.ordered_answers(answers, possibles, count)

# testing
if __name__ == '__main__':

    if False:
        print('false')

    if True:
        num = 100
        qp = QuestionProcessor()
        qp.set_question('Where did Woodstock take place?')
        pr = PassageRetriever()
        pr.set_question(18, qp.get_keywords(), 'train', 20)
        all_passages = pr.retrieve_top_scored_passages(1000)
        print (all_passages)
        af = AnswerFormulator()
        af.set_question(qp.get_question(), all_passages)
        print (af.get_answers())
