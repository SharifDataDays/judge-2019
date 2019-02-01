from configuration import QuestionType as Qt
import logger
import json
import configuration as config

import random

# FIXME !WORK IN PROGRESS!

answers_dict = None

def get_question_result_from_db(team_id, question_id, question_type):
    global answers_dict
    logger.log_info("getting question answers from db", team_id, question_id)
    if answers_dict is None:
        with open(config.ANSWERS_FILE_PATH) as f:
            answers_dict = json.load(f)
    
    return answers_dict[str(question_id)]

def score(team_id, question_id, phase_id, dataset_number, question_type, submitted_answer):
    logger.log_info("judging", team_id, question_id, question_type)
    real_answer = get_question_result_from_db(team_id, question_id, question_type)

    # submitted_answer and real_answer are strings retrieved from db and request without modification
    return FUNCTION_MAP[question_type](team_id, submitted_answer, real_answer)


def score_multiple_choice(team_id, submitted_answer, real_answer):
    return score_single_answer(team_id, submitted_answer, real_answer)

def score_file_upload(team_id, submitted_answer, real_answer):
    with open(submitted_answer, mode='r') as read_file:
        submitted_categories = read_file.readlines()

    tidy_submitted_categories = []
    for line in submitted_categories:
        if line.strip() == '':
            continue
        tidy_submitted_categories.append(line.strip().lower())

    with open(real_answer, mode='r') as read_file:
        real_categories = read_file.readlines()

    tidy_real_categories = []
    for line in real_categories:
        if line.strip() == '':
            continue
        tidy_real_categories.append(line.strip().lower())

    if len(tidy_real_categories) != len(tidy_submitted_categories):
        logger.log_warn("invalid number of categories", team_id)
        return 0.0
    else:
        total_count = len(tidy_real_categories)
        correct_count = 0
        for i in range(total_count):
            if tidy_real_categories[i] == tidy_submitted_categories[i]:
                correct_count += 1

        return correct_count / total_count

def score_single_answer(team_id, submitted_answer, real_answer):
    submitted_answer = submitted_answer.strip().lower()
    real_answer = real_answer.strip().lower()
    print('\033[92m"{}" "{}"\033[0m'.format(submitted_answer, real_answer))
    result = 0.0
    if submitted_answer == real_answer:
        result = 1.0

    return result


def score_multiple_answer(team_id, submitted_answer, real_answer):
    submitted_answer = submitted_answer.strip().split('$')
    submitted_answer = [x.strip().lower() for x in submitted_answer]

    real_answer = real_answer.strip().split('$')
    real_answer = [x.strip().lower() for x in real_answer]

    real_answer_count = len(real_answer)
    correct_answer_count = len(set(real_answer).intersection(set(submitted_answer)))

    return correct_answer_count / real_answer_count



def score_single_sufficient_answer(team_id, submitted_answer, real_answer):
    return score_multiple_answer(team_id, submitted_answer, real_answer)


def score_single_number(team_id, submitted_answer, real_answer):
    try:
        submitted_answer = float(submitted_answer.strip())
    except ValueError:
        logger.log_warn("invalid float response", team_id)
        return 0.0

    real_answer = float(real_answer.strip())
    
    result = 0.0
    if submitted_answer == real_answer:
        result = 1.0

    return result


def score_interval_number(team_id, submitted_answer, real_answer):
    try:
        submitted_answer = float(submitted_answer.strip())
    except ValueError:
        logger.log_warn("invalid float response", team_id)
        return 0.0

    lower_bound, upper_bound = [float(x.strip()) for x in real_answer.strip().split('$')]
    #if lower_bound > upper_bound:
    #     lower_bound, upper_bound = upper_bound, lower_bound

    result = 0.0
    if lower_bound <= submitted_answer <= upper_bound:
        result = 1.0

    return result


def score_single_suffiient_answer(submitted_answer, real_answer):
    pass


def score_single_number_answer(submitted_answer, real_answer):
    pass


def score_interval_number_answer(submitted_answer, real_answer):
    pass


FUNCTION_MAP = {
    Qt.MULTIPLE_CHOICE.value: score_multiple_choice,
    Qt.FILE_UPLOAD.value: score_file_upload,
    Qt.SINGLE_ANSWER.value: score_single_answer,
    Qt.MULTIPLE_ANSWER.value: score_multiple_answer,
    Qt.SINGLE_SUFFICIENT_ANSWER.value: score_single_sufficient_answer,
    Qt.SINGLE_NUMBER.value: score_single_number,
    Qt.INTERVAL_NUMBER.value: score_interval_number,
}
