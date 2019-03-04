from configuration import QuestionType as Qt, PHASE_2_ANSWERS_PATH
import logger
import json
import configuration as config
from chardet import detect
import pandas as pd
import numpy as np

import random

PHASE_3_ANSWERS_PATH = '<phase 3 answers csv file path here>'

CITY_NAME_TRANSLATIONS = {
    'Tehran': 'تهران',
    'tehran': 'تهران',
    'Mashhad': 'مشهد',
    'mashhad': 'مشهد',
    'Karaj': 'کرج',
    'karaj': 'کرج',
    'Qom': 'قم',
    'qom': 'قم',
    'Isfahan': 'اصفهان',
    'isfahan': 'اصفهان',
    'Shiraz': 'شیراز',
    'shiraz': 'شیراز',
    'Tabriz': 'تبریز',
    'tabriz': 'تبریز',
    'Ahvaz': 'اهواز',
    'ahvaz': 'اهواز',
    'Kermanshah': 'کرمانشاه',
    'kermanshah': 'کرمانشاه',
}

def boolean_value_cast(in_str):
    if in_str.strip().lower() == 'true':
        return True
    return False

answers_dict = None

SCORE_A1 = 0.1
SCORE_A2 = 0.0
SCORE_A3 = 0.9

logger.log_info('loading phase 2 answers...')
PHASE_2_ANSWERS = [x[1] for x in pd.read_csv(PHASE_2_ANSWERS_PATH, low_memory=False)[['cat1', 'cat2', 'cat3']].iterrows()]
logger.log_info('loaded phase 2 answers...')

logger.log_info('loading phase 3 answers...')

_tmp = pd.read_csv(PHASE_3_ANSWERS_PATH, low_memory=False)
_tmp.columns = ['answer', 'score']
_tmp['answer'] = _tmp['answer'].apply(boolean_value_cast)

PHASE_3_ANSWERS = [x[1] for x in _tmp.iterrows()]
PHASE_3_TOT_SCORE = np.array([float(x['score']) for x in PHASE_3_ANSWERS]).sum()
logger.log_info('loaded phase 3 answers...')





def get_question_result_from_db(team_id, question_id, question_type):
    global answers_dict
    logger.log_info("getting question answers from db", team_id, question_id)
    if answers_dict is None:
        with open(config.ANSWERS_FILE_PATH) as f:
            answers_dict = json.load(f)
    logger.log_info("got question answers from db", team_id, question_id)
    try:
        return answers_dict[str(question_id)]
    except:
        return None


def score(team_id, question_id, phase_id, dataset_number, question_type, submitted_answer):
    try:
        logger.log_info("judging", team_id, question_id, question_type)
        if question_type != 'triple_cat_file_upload':
            real_answer = get_question_result_from_db(team_id, question_id, question_type)
        else:
            real_answer = 0

        ret = FUNCTION_MAP[question_type](team_id, submitted_answer, real_answer)

        logger.log_info("Answer checked", team_id, question_id)
        return ret
    except:
        logger.log_error("score_function_error", team_id, question_id, question_type)
        if question_type == 'triple_cat_file_upload':
            return [0, 0]
        else:
            return 0


def score_multiple_choice(team_id, submitted_answer, real_answer):
    return score_single_answer(team_id, submitted_answer, real_answer)


def score_file_upload(team_id, submitted_answer, real_answer):
    with open(submitted_answer, mode='rb') as binary_read_file:
        file_encoding = detect(binary_read_file.read())

    with open(submitted_answer, encoding=file_encoding['encoding']) as read_file:
        submitted_categories = read_file.readlines()

    tidy_submitted_categories = []
    for line in submitted_categories:
        tidy_submitted_categories.append(line.strip().lower())

    with open(real_answer, mode='rb') as binary_read_file:
        answer_file_encoding = detect(binary_read_file.read())

    with open(real_answer, encoding=answer_file_encoding['encoding']) as read_file:
        real_categories = read_file.readlines()

    tidy_real_categories = []
    for line in real_categories:
        tidy_real_categories.append(line.strip().lower())

    if len(tidy_real_categories) > len(tidy_submitted_categories):
        logger.log_warn("not enough lines in submission", team_id)
        return 0.0
    
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

    if submitted_answer in CITY_NAME_TRANSLATIONS:
        submitted_answer = CITY_NAME_TRANSLATIONS[submitted_answer]

    if submitted_answer == real_answer:
        result = 1.0

    return result


def score_multiple_answer(team_id, submitted_answer, real_answer):
    submitted_answer = submitted_answer.strip().split('$')
    submitted_answer = [x.strip().lower() for x in submitted_answer]

    new_answers = []
    for answer in submitted_answer:
        if answer in CITY_NAME_TRANSLATIONS:
            new_answers.append(CITY_NAME_TRANSLATIONS[answer])
        else:
            new_answers.append(answer)

    submitted_answer = new_answers

    real_answer = real_answer.strip().split('$')
    real_answer = [x.strip().lower() for x in real_answer]

    real_answer_count = len(real_answer)
    correct_answer_count = len(set(real_answer).intersection(set(submitted_answer)))

    logger.log_info('score_multiple_answer', float(correct_answer_count / real_answer_count),
                    submitted_answer, real_answer)

    return correct_answer_count / 3


def score_single_sufficient_answer(team_id, submitted_answer, real_answer):
    return score_multiple_answer(team_id, submitted_answer, real_answer)


def score_single_number(team_id, submitted_answer, real_answer):
    logger.log_info("entered score single number", team_id)
    try:
        submitted_answer = float(submitted_answer.strip())
    except ValueError:
        logger.log_warn("invalid float response", team_id)
        return 0.0

    logger.log_info("calculating real answer", team_id)
    logger.log_info("submitted_answer is {}, real answer is {}".format(submitted_answer, real_answer), team_id);
    real_answer = float(real_answer)
    
    result = 0.0
    if submitted_answer == real_answer:
        result = 1.0

    logger.log_info("result evaluated", team_id)
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


def score_triple_cat_file_upload(team_id, submitted_answer, real_answer):

    try:
        submitted_categories = [x[1] for x in pd.read_csv(submitted_answer, low_memory=False).iterrows()]
    except:
        logger.log_warn("malformed csv file", team_id)
        return [0.0, 0.0]

    if len(submitted_categories) < len(PHASE_2_ANSWERS):
        logger.log_warn("not enough lines in submission", team_id)
        return [0.0, 0.0]

    score_1 = 0
    n_tot = len(PHASE_2_ANSWERS)

    for i in range(n_tot//2):
        score_1 += _score_cats(submitted_categories[i], PHASE_2_ANSWERS[i])

    score_1 = score_1 / (n_tot//2) / 0.8732799999997414

    score_2 = 0
    for i in range(n_tot//2, n_tot):
        score_2 += _score_cats(submitted_categories[i], PHASE_2_ANSWERS[i])

    score_2 = score_2 / (n_tot - n_tot//2) / 0.8737679999997485

    return [score_1, score_2]
        
        
def _score_cats(submitted_cats, answer_cats):
    score = 0

    if submitted_cats['cat1'] == answer_cats['cat1']:
        score += SCORE_A1
        if submitted_cats['cat2'] == answer_cats['cat2']:
            score += SCORE_A2
            if submitted_cats['cat3'] == answer_cats['cat3']:
                score += SCORE_A3
                return score
            else:
                return score
        else:
            return score
    else:
        return score


#    if not pd.isna(answer_cats['cat2']):
#        if submitted_cats['cat2'] == answer_cats['cat2']:
#            score += SCORE_A2
#        else:
#            return score
#
#        if not pd.isna(answer_cats['cat3']):
#            if submitted_cats['cat3'] == answer_cats['cat3']:
#                score += SCORE_A3
#        else:
#            if pd.isna(submitted_cats['cat3']):
#                score += SCORE_A3
#    else:
#        if pd.isna(submitted_cats['cat2']):
#            score += SCORE_A2
#        if pd.isna(submitted_cats['cat3']):
#            score += SCORE_A3
#
#    return score

def score_boolean_file_upload(team_id, submission_path, _):
    try:
        submission = pd.read_csv(submission_path, low_memory=False)
        submission.columns = ['answer']
        submission['answer'] = submission['answer'].apply(boolean_value_cast)
    except:
        logger.log_warn("malformed csv file", team_id)
        return 0.0

    if len(submission) < len(PHASE_3_ANSWERS):
        logger.log_warn("not enough lines in submission", team_id)
        return 0.0

    score = 0.0
    for i in range(len(PHASE_3_ANSWERS)):
        if submission.iloc[i]['answer'] == PHASE_3_ANSWERS[i]['answer']:
            score += PHASE_3_ANSWERS[i]['score']

    return score / PHASE_3_TOT_SCORE


FUNCTION_MAP = {
    Qt.MULTIPLE_CHOICE.value: score_multiple_choice,
    Qt.FILE_UPLOAD.value: score_file_upload,
    Qt.SINGLE_ANSWER.value: score_single_answer,
    Qt.MULTIPLE_ANSWER.value: score_multiple_answer,
    Qt.SINGLE_SUFFICIENT_ANSWER.value: score_single_sufficient_answer,
    Qt.SINGLE_NUMBER.value: score_single_number,
    Qt.INTERVAL_NUMBER.value: score_interval_number,
    Qt.TRIPLE_CAT_FILE_UPLOAD.value: score_triple_cat_file_upload,
    Qt.BOOLEAN_FILE_UPLOAD.value: score_boolean_file_upload,
}
