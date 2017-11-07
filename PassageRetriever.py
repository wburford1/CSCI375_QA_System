from collections import namedtuple
import nltk

ScoredPassage = namedtuple('ScoredPassage', 'passage, score, passage_str')
TextPassagesScored = namedtuple('TextPassagesScored', 'rank, score, scored_passages')


class PassageRetriever:
    def __init__(self):
        self.question_number = None
        self.keywords = None
        self.environment = None
        self.gram_length = None

    # question_number is the Qid
    # keywords is an array of terms to be queried. This will be used as a feature vector
    # environment will be either 'train' or 'test'
    def set_question(self, question_number, keywords, environment='train', gram_length=10):
        self.question_number = question_number
        self.keywords = keywords
        self.environment = environment
        self.gram_length = gram_length

    def clear_question(self):
        self.question_number = None
        self.keywords = None
        self.environment = None
        self.gram_length = None

    def retrieve_text_passages_scored(self):
        # latin-1 ??????
        with open('topdocs/{}/top_docs.{}'.format(self.environment, self.question_number),
                  'r', encoding='latin-1') as top_docs_file:
            top_docs = top_docs_file.read()
            docs = top_docs.split('Qid: ')
            text_passages_scored = []
            docs.remove("")
            for doc in docs:
                # if self.question_number == 17:
                #     print('--------------------------------')
                #     print(doc)
                text = None
                if '<TEXT>' in doc:
                    text = doc.split('<TEXT>')[1]
                    text = doc.split('</TEXT>')[0]
                elif '<LEADPARA>' in doc:
                    text = doc.split('<LEADPARA>')[1]
                    text = doc.split('</LEADPARA>')[0]
                # else:
                    # print(doc)
                    # print("Cannot find body text of document.")
                    # raise Exception("Cannot find body text of document.")
                if text is not None:
                    rank = (int)(doc[doc.index('Rank: ')+len('Rank: '): doc.index('Score: ')])
                    score = (float)(doc[doc.index('Score: ')+len('Score: '): doc.index('\n')])
                    scored_passages = self.score_passages_from_text(text)
                    scored_passages = sorted(scored_passages, key=lambda passage: passage.score)
                    text_passages_scored.append(TextPassagesScored(rank, score, scored_passages))
            return text_passages_scored

    # count is the number of passages to be retrieved. If None, all passages will be retrieved
    def retrieve_top_scored_passages(self, count=None):
        text_passages_scored = self.retrieve_text_passages_scored()
        all_passages = []
        for text_tup in text_passages_scored:
            scored_passages = text_tup.scored_passages
            for scored_passage in scored_passages:
                composite_score = scored_passage.score * (text_tup.score/100)
                all_passages.append(ScoredPassage(scored_passage.passage, composite_score, scored_passage.passage_str))
        all_passages = sorted(all_passages, key=lambda passage: -1*passage.score)
        return all_passages[0: min(count, len(all_passages))] if count is not None else all_passages

    def score_passages_from_text(self, text):
        passages = self.get_passages_from_text(text)
        feature_vector = {key: 0 for key in self.keywords}
        found_keyword = False
        scored_passages = []
        for passage_and_recomb in passages:
            passage = passage_and_recomb[0]
            for key in feature_vector:
                if key in passage:
                    feature_vector[key] = 1  # using binary feature vector
                    found_keyword = True
            similarity = (self.cosine_similarity(list(feature_vector.values()),
                                                 [1 for _ in range(0, len(feature_vector), 1)])
                          if found_keyword else 0)
            scored_passages.append(ScoredPassage(passage, similarity, passage_and_recomb[1]))
            # clear feature_vector
            if found_keyword:
                for key in feature_vector:
                    feature_vector[key] = 0
                found_keyword = False
        return scored_passages

    def get_passages_from_text(self, text):
        tokens = nltk.word_tokenize(text)
        # ~A
        assert len(tokens) >= self.gram_length
        passages = [tokens[index: index+self.gram_length] for index in range(0, len(tokens)-10, 1)]
        recombined = [" ".join(passage) for passage in passages]
        for recomb in recombined:
            recomb = recomb.replace(" .", ".")
            recomb = recomb.replace(' ?', "?")
            recomb = recomb.replace(' !', "!")
        return [(passages[i], recombined[i]) for i in range(0, len(passages), 1)]

        # sentences = nltk.sent_tokenize(text)
        # tok_sentences = [nltk.word_tokenize(sent) for sent in sentences]
        # return [(tok_sentences[i], sentences[i]) for i in range(0, len(sentences), 1)]

    @staticmethod
    def cosine_similarity(vector1, vector2):
        assert len(vector1) == len(vector2)
        dot_prod = sum([vector1[i]*vector2[i] for i in range(0, len(vector1), 1)])
        mag1_squared = sum([vector1[i]**2 for i in range(0, len(vector1), 1)])
        mag2_squared = sum([vector2[i]**2 for i in range(0, len(vector2), 1)])
        return dot_prod / ((mag1_squared * mag2_squared)**(1/2))


# run tests on PassageRetriever
if __name__ == '__main__':
    if False:
        print('cosine sim test')
        sim = PassageRetriever.cosine_similarity([1, 1, 1, 1], [1, 1, 0, 0])
        print('Cosine sim = {}'.format(sim))
    if True:
        print('Question 0 test')
        keywords = ['hockey', 'team', 'Wayne', 'Gretzky', 'play']
        retriever = PassageRetriever()
        retriever.set_question(0, keywords, 'train', 20)
        all_passages = retriever.retrieve_top_scored_passages()
        top_passages = all_passages[0:10]
        counter = 1
        for passage in top_passages:
            print("{}. {} scored {}".format(counter, passage.passage, passage.score))
            counter += 1
        print("looking for Kings in a passage...")
        counter = 0
        for passage in all_passages:
            if "Kings" in passage.passage:
                print("Found 'Kings' in {} index package with score {}.".format(counter, passage.score))
                break
            counter += 1


# potential improvements
# at ~A: could experiment with grouping tokens together, whole sentences as passages
# add morphological matching to feature vectors
