from enum import Enum

JUDGE_SERVER_HOST = '0.0.0.0'
JUDGE_SERVER_PORT = 9098
TEST_TIMEOUT_S = 60
RUN_TIMEOUT_S = 60
ACCESS_TIMEOUT_S = 5

REPORT_SERVER_HOST = 'localhost'
REPORT_SERVER_PORT = 8000
REPORT_SERVER_PATH = 'dsvfghjsehtdryjfuihlxdfgchjkl/'

JUDGE_MANDATORY_REQUEST_FIELDS = ['team_id', 'phase_id', 'trial_id', 'dataset_number', 'submissions']
SUBMISSION_MANDATORY_FIELDS = ['question_id', 'question_type', 'submitted_answer']

ANSWERS_FILE_PATH = '/home/mrtaalebi/projects/backend-2019/json_answers.json'


class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILE_UPLOAD = "file_upload"
    SINGLE_ANSWER = "single_answer"
    MULTIPLE_ANSWER = "multiple_answer"
    SINGLE_SUFFICIENT_ANSWER = "single_sufficient_answer"
    SINGLE_NUMBER = "single_number"
    INTERVAL_NUMBER = "interval_number"

    @classmethod
    def list_types(cls):
        return [x.lower() for x in list(cls._member_map_.keys())]
