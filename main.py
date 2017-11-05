import QuestionProcessor
import PassageRetriever
import AnswerFormulator
from collections import namedtuple

Question = namedtuple('Question', 'question, number')


def main():
    qp = QuestionProcessor.QuestionProcessor()
    pr = PassageRetriever.PassageRetriever()
    af = AnswerFormulator.AnswerFormulator()
    questions = []

    with open('qadata/train/questions.txt', 'r') as questions_file:
        q_lines = questions_file.readlines()
        index = 0
        while index < len(q_lines):
            line = q_lines[index]
            if line.startswith('Number: '):
                q_num = int(line[len("Number: "):])
                quest = q_lines[index+1].replace('\n', '')
                questions.append(Question(quest, q_num))
                index += 1
            index += 1
        print(questions)



if __name__ == '__main__':
    main()
