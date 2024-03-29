import QuestionProcessor
import PassageRetriever
import AnswerFormulator
from collections import namedtuple
import config

Question = namedtuple('Question', 'q, num')


def main():
    qp = QuestionProcessor.QuestionProcessor()
    pr = PassageRetriever.PassageRetriever()
    af = AnswerFormulator.AnswerFormulator()
    questions = []

    with open(config.QUESTION_FILE_PATH, 'r') as questions_file:
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
        # print(questions)

        with open('predictions.txt', 'w') as pred_file:
            for quest_obj in questions:
                keywords = qp.find_keywords(quest_obj.q)
                pr.clear_question()
                pr.set_question(quest_obj.num, keywords, 15)
                passage_objs = pr.retrieve_top_scored_passages()
                print('Question {}'.format(quest_obj.num))
                print("\t{} --> {}".format(quest_obj.q, keywords))
                print("\tBest passage: {}. Score = {}".format(passage_objs[0].passage, passage_objs[0].score))

                af.set_question(quest_obj.q, passage_objs)
                answers = af.get_answers()
                pred_file.write('qid {}\n'.format(quest_obj.num))
                for ans in answers:
                    pred_file.write(str(ans)+'\n')
                for i in range(len(answers), 10, 1):
                    pred_file.write(str("no answer {}\n".format(i)))


if __name__ == '__main__':
    main()
