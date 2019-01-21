from configuration import QuestionType as QT

FUNCTION_MAP = {
    QT.MULTIPLE_CHOICE.value: score_multiple_choice,
    QT.FILE_UPLOAD.value: score_file_upload,
    QT.TRUE_FALSE.value: score_true_false,
    QT.SINGLE_ANSWER.value: score_single_answer,
    QT.MULTIPLE_ANSWER.value: score_multiple_answer,
}

def score(question_id, phase_id, dataset_number, question_type, submitted_answer):

    real_answer = None # TODO CALCULATE REAL ANSWER FROM question_id, phase_id, dataset_number
    return FUNCTION_MAP[question_type](submitted_answer, real_answer)

def score_multiple_choice(submitted_answer, real_answer):
    pass

def score_file_upload(submitted_answer, real_answer):
    pass

def score_true_false(submitted_answer, real_answer):
    pass

def score_single_answer(submitted_answer, real_answer):
    pass

def score_multiple_answer(submitted_answer, real_answer):
    pass