# Nevin Bernet

import nltk
from nltk import ne_chunk, pos_tag, word_tokenize, Text
from nltk.chunk import tree2conlltags
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from QuestionProcessor import QuestionProcessor
from PassageRetriever import PassageRetriever
import re
import collections
import time
import timex
import similarity
import string

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
        self.qp = QuestionProcessor()

    # question is a string, passages is a list of passage objects defined in PassageRetriever
    def set_question(self, question, passages):
        self.clear()
        self.question = question
        self.tokenized_q = word_tokenize(question)
        self.ne_tagged_q = tree2conlltags(ne_chunk(pos_tag(self.tokenized_q)))
        self.passage_objs = passages
        self.qp.set_question(self.question)

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

        if 'name' in self.question.lower():
            return 'NAME'
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
            if (self.tokenized_q[1] == "'s" or 'is' in self.tokenized_q or 'are' in self.tokenized_q or 'was' in self.tokenized_q or 'were' in self.tokenized_q):
                return ['DEF']
            else:
                return['CHARACTERISTIC']
        elif qt == 'WHICH':
            return ['ELEMENTOF']
        elif qt == 'HOW':
            if self.qp.get_keywords()[self.qp.get_keywords().index(qt.lower()) + 1] in ['much', 'many', 'few']:
                return ['AMOUNT']


    # returns an array of ten answers where [0] is the 'best' answer and [9] is the tenth best
    # question and passages must not be equal to None
    def get_answers(self, count=10):

        possible_answers = {}
        at = self.get_answertype()
        stopword_set = set(stopwords.words('english'))

        # narrow down the number of passages we need to search
        print('{} passages'.format(len(self.passage_objs)))
        start_time = time.time()

        # START WHEN LOOKING FOR NAMED ENTITY ANSWER
        # if we are looking for a specific named entity, make sure we have that named entity in one of the passages
        if at is None:
            print('No answer type for question: {}'.format(self.question))
            return []
        at_is_ne = False
        for a_type in at:
            if a_type in ['ORGANIZATION', 'PERSON', 'LOCATION', 'MONEY', 'PERCENT', 'FACILITY', 'GPE']:
                at_is_ne = True
                break
        # only do ne tagging if we are looking for a named entity as the answer
        if at_is_ne:
            end_ne_tagging_index = 2000
            # not_stopwords_passages = [[e for e in element.passage if e not in stopword_set] for element in self.passage_objs]
            # tagged passages is has an IOB tagged passage at [0] and the passage obj at [1]
            tagged_passages = [([e for e in tree2conlltags(ne_chunk(pos_tag(element.passage))) if not e[2] == 'O'], element) for element in self.passage_objs[:end_ne_tagging_index]]
            ne_passages = [e for e in tagged_passages if not len(e[0]) == 0]
            found_correct_ne = False
            while not found_correct_ne and end_ne_tagging_index <= len(self.passage_objs):
                for ne_pass in ne_passages:
                    for ne in ne_pass[0]:
                        if ne[2][ne[2].index('-')+1:] in at:
                            found_correct_ne = True
                            break
                    if found_correct_ne:
                        break
                if not found_correct_ne:
                    print('had to increment')
                    increment_amount = 1000
                    tagged_passages = [([e for e in tree2conlltags(ne_chunk(pos_tag(element.passage))) if not e[2] == 'O'], element) for element in self.passage_objs[end_ne_tagging_index:min(end_ne_tagging_index + increment_amount, len(self.passage_objs))]]
                    end_ne_tagging_index += increment_amount
                    ne_passages += [e for e in tagged_passages if not len(e[0]) == 0]

            print("NE tagging took {}s".format(time.time()-start_time))

            # these will only occur when an answer type is in a named entity
            if self.get_questiontype() in ['WHO', 'WHERE', 'NAME']:
                # goes through every named entity in the passages and if a given named entity's type is in at then it adds that answer to possible answers or increments that answer's score by 1 if it already exists in possible aswers
                for passage in ne_passages:
                    for e in passage[0]:
                        #second part of this if statement because otherwise this will often return the subject of the question as the answer... ie who owns cnn will return cnn
                        if e[2][e[2].index('-') + 1:] in at and e[0] not in self.tokenized_q:
                            if e[0] not in possible_answers:
                                possible_answers[e[0]] = passage[1].score
                            else:
                                possible_answers[e[0]] += passage[1].score
        # if we are looking for a time/date, use timex
        # it only recognizes years and relative time statements though (need a Python 2 module to do better things)
        # this seems to be ok for now though b/c I only see WHEN Qs with year answers
        elif 'TIME' in at or 'DATE' in at:
            last_time_tagged_index = 5000
            time_tagged = [(timex.tag(pass_obj.passage_str), pass_obj) for pass_obj in self.passage_objs[:last_time_tagged_index]]
            for t_pass in time_tagged:
                if "<TIMEX2>" in t_pass[0] and "</TIMEX2>" in t_pass[0]:
                    time_entity = t_pass[0][t_pass[0].index('<TIMEX2>')+len('<TIMEX2>'):t_pass[0].index('</TIMEX2>')]
                    if time_entity not in possible_answers:
                        possible_answers[time_entity] = t_pass[1].score
                    else:
                        possible_answers[time_entity] += t_pass[1].score
        # END LOOKING FOR NAMED ENTITY ANSWER

        elif 'DEF' in at:
            end_passages = 2000
            to_be = ['is', 'are', 'were', 'was']
            mod_tok_q = None
            if "'s" == self.tokenized_q[1]:
                mod_tok_q = self.tokenized_q[2:]
            for be in to_be:
                if be in self.tokenized_q:
                    mod_tok_q = list(self.tokenized_q)
                    mod_tok_q.pop(mod_tok_q.index(be))
            if '?' in mod_tok_q:
                mod_tok_q.pop(mod_tok_q.index('?'))
            if 'what' == mod_tok_q[0].lower():
                mod_tok_q.pop(0)
            for be in to_be:
                # for i in range(0, len(mod_tok_q), 1):
                #     more_modified_toks = list(mod_tok_q)
                #     more_modified_toks.insert(i, be)
                mod_tok_q.append(be)
                for passage_obj in self.passage_objs[:end_passages]:
                    pas = passage_obj.passage
                    pas_pos = pos_tag(pas)
                    for pos in pas_pos:
                        if (pos[1] == 'NN' or pos[1] == 'NNS') and pos[0] not in mod_tok_q:
                            if pos[0] not in possible_answers:
                                possible_answers[pos[0]] = passage_obj.score
                            else:
                                possible_answers[pos[0]] += passage_obj.score
                    joined_pas = " ".join(pas)
                    if " ".join(mod_tok_q) in joined_pas:
                        last_word = mod_tok_q[len(mod_tok_q)-1]
                        phrase = []
                        for i in range(pas.index(last_word), len(pas), 1):
                            pos = pas_pos[i]
                            if (pos[1] == 'NN' or pos[1] == 'NNS') and pos[0] not in mod_tok_q:
                                phrase.append(pos[0])
                            if not (pos[1] == 'NN' or pos[1] == 'NNS'):
                                break
                        if len(phrase) > 0:
                            answer = " ".join(phrase)
                            print('found answer = {}'.format(answer))
                            possible_answers[answer] = 1

                mod_tok_q = mod_tok_q[:len(mod_tok_q)-1]

        else:
            possible_answers = self.satisfies_patterns(at)

        return self.ordered_answers([], possible_answers, count)

    # A method for finding finding patterns in the passages
    # returns a dictionary of Strings found in the passages linked to the confidence in each String, where each String satisfies a pattern corresponding to 'pattern_type'
    def satisfies_patterns(self, pattern_type):

        possibles = {}

        if 'DEF' in pattern_type:
            all_patterns = []
            def_patterns = '<SUBJECT> is a .+|.+ such as <SUBJECT>|<SUBJECT> are .+|<SUBJECT> , .+ ,|> .+ such as the <SUBJECT>| .+ such as a <SUBJECT>'
            for word in self.qp.get_keywords():
                if word.upper() == self.get_questiontype():
                    subject = self.qp.get_keywords()[self.qp.get_keywords().index(word) + 1]
                    break
            subject = subject.lower()
            def_patterns = def_patterns.replace('<SUBJECT>', subject)

            #goes through all passages and finds any substrings of each passage that match the above defined patterns, then adds the the non-stopword, non-punctuation tokens of each pattern to the dictionary with the value of the passage score
            for passage in self.passage_objs:
                for match in re.findall(def_patterns, passage.passage_str, re.IGNORECASE):
                    for token in [word.lower() for word in nltk.word_tokenize(match) if word not in set(stopwords.words('english')) and word not in list(string.punctuation) and not word.lower() == subject]:
                        if token not in possibles:
                            possibles[token] = passage.score
                        else:
                            possibles[token] += passage.score

        #elif '' in pattern_type:


        return possibles

    # recursive method for ordering answers 1-count given a number of possible answers
    # 'possibilities' is a dictionary of answer:confidence where confidence is a quantified measure of increasing confidence in the answer
    # returns a list of answers in order from best to worst of length count OR the max possible length given the number of possible answers
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
        # test_qs = [('Where did Woodstock take place?', 18),
        #            ('Who is the founder of the Wal-Mart stores?', 41),
        #            ('Who created "The Muppets"?', 62),
        #            ('Name a civil war battlefield.', 75),
        #            ('When did the California lottery begin?', 104),
        #            ('What is thalassemia?', 15),
        #            ('What is a stratocaster', 39),
        #            ('What are the Poconos?', 55)]
        test_qs = [('What are the Poconos?', 55),
                   ("What's the most famous tourist attraction in Rome?", 66),
                   ("What province is Edmonton located in?", 102)]
        for test_q in test_qs:
            print(test_q)
            qp.set_question(test_q[0])
            pr = PassageRetriever()
            pr.set_question(test_q[1], qp.get_keywords(), 10)
            all_passages = pr.retrieve_top_scored_passages()
            # print(all_passages)
            af = AnswerFormulator()
            af.set_question(qp.get_question(), all_passages)
            print(af.get_answers())
