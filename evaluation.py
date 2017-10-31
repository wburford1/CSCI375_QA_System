"""
Usage: python evaluation.py answer-pattern-file prediction-file 

Prediction file format : 
qid 100
Answer1
Answer2
...
Answer10
qid 102
Answer1
Answer2
Answer3
qid 130
...

You may provide any number of answers for each question, but everything beyond the 10th one will be ignored. Also, qids that appear in the respective answer_patterns.txt, but are not present in the prediction file are regarded as incorrectly answering the question.
"""
import re
import sys

def read_answer_patterns(pattern_file_path):
    """read answer patterns into qid2patterns dictionary
    """
    qid2patterns = {}

    last_qid = None
    with open(pattern_file_path) as f:
        for line in f : 
            [qid,pattern] = line.strip().split("\t")
            if qid == last_qid : 
                patterns.append(pattern)
            elif last_qid == None: # first question
                last_qid = qid
                patterns = [pattern]
            else : # new question
                qid2patterns[last_qid] = patterns

                last_qid = qid
                patterns = [pattern]

    qid2patterns[last_qid] = patterns
    return qid2patterns

SUCCESS_STR = "qid {:s}: Correct prediction {:s} at rank {:d}"
QID_STR = "qid "
QID_IDX = len(QID_STR)
def evaluate(prediction_file_path,qid2patterns):
    """evaluate the prediction file
    """
    total_score = 0
    solution_found = True # do nothing until the first qid is seen
    with open(prediction_file_path) as f:
        for line in f: 
            line = line.strip()
            if len(line) == 0: # ignore empty lines
                continue

            if line.startswith(QID_STR): # new question
                qid = line[QID_IDX:]
                rank = 0
                solution_found = False
            elif not solution_found and rank < 10:
                rank += 1
                prediction = line

                #check if the prediction matches an answer pattern
                patterns = qid2patterns[qid]
                for pattern in patterns: 
                    p = re.compile(pattern, re.IGNORECASE)
                    if p.match(prediction) : 
                        total_score += (1.0/rank)
                        print(SUCCESS_STR.format(qid,prediction,rank))
                        solution_found = True
                        break

    return total_score/len(qid2patterns) # total_score / # of questions

if __name__ == "__main__":
    pattern_file = str(sys.argv[1])
    prediction_file = str(sys.argv[2])

    qid2patterns = read_answer_patterns(pattern_file)
    mrr = evaluate(prediction_file,qid2patterns)

    print("\n# of questions: {:d}".format(len(qid2patterns)))
    print("MRR: {:4f}".format(mrr))
