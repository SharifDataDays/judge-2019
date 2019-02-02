import json
import sys
from datetime import datetime, timedelta
from threading import Thread

import requests
from flask import Flask, request

import configuration as config
import logger as logger
from score_functions import score

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    print("AAAAAAAAAAAAAAAAAAA")
    print(request.__dict__)
    print("BBBBBBBBBBBBBBBBBBB")
    print(request.get_json())
    print("CCCCCCCCCCCCCCCCCCC")
    print(str(request.get_json()))

    request_data = request.get_json()

    for field in config.JUDGE_MANDATORY_REQUEST_FIELDS:
        if field not in request_data:
            error_message = 'malformed post request data, excepting field {}'.format(field)
            logger.log_error(error_message)
            return error_message, 400

    submissions = request_data['submissions']

    for submission in submissions:
        for field in config.SUBMISSION_MANDATORY_FIELDS:
            if field not in submission:
                error_message = 'malformed post request data, excepting submission field {}'.format(field)
                logger.log_error(error_message)
                return error_message, 400

        if submission['question_type'] not in config.QuestionType.list_types():
            error_message = 'malformed post request data, invalid question type: {}'.format(submission['question_type'])
            logger.log_error(error_message)
            return error_message, 400

    team_id = request_data['team_id']

    logger.log_info('lock acquired for team with team_id {}'.format(team_id))

    phase_id = request_data['phase_id']
    trial_id = request_data['trial_id']
    dataset_number = request_data['dataset_number']

    process_request(team_id, phase_id, trial_id, dataset_number, submissions)
    logger.log_success(
        'test for team with team_id {} initiated successfully'.format(team_id))
    return "success - test initiated", 200


def process_request(team_id, phase_id, trial_id, dataset_number, submissions):
    thread = Thread(target=worker_function, args=(team_id, phase_id, trial_id, dataset_number, submissions))
    thread.start()


def worker_function(team_id, phase_id, trial_id, dataset_number, submissions):
    logger.log_info('scoring submission for team with team_id {}.'.format(team_id))
    question_scores = worker_score_questions(team_id, phase_id, dataset_number, submissions)
    logger.log_info('reporting test results for team with team_id {}, to competition server'.format(team_id))
    report_test_results(team_id, phase_id, trial_id, dataset_number, question_scores)
    logger.log_success('test for team with team_id {} finished successfully'.format(team_id))


def worker_score_questions(team_id, phase_id, dataset_number, submissions):
    question_scores = []

    for question in submissions:
        question_id = question['question_id']
        question_type = question['question_type']
        submitted_answer = question['submitted_answer']

        question_score = score(team_id, question_id, phase_id, dataset_number, question_type, submitted_answer)

        question_scores.append({
            'question_id': question_id,
            'score': question_score
        })

    return question_scores


def report_test_results(team_id, phase_id, trial_id, dataset_number, question_scores):
    judge_report = {
        'team_id': team_id,
        'phase_id': phase_id,
        'trial_id': trial_id,
        'dataset_number': dataset_number,
        'submissions': question_scores
    }
    logger.log_log('log report for team with team_id {}'.format(team_id))
    logger.log_log(judge_report)

    requests.post(
        'https://{}:{}/{}'.format(config.REPORT_SERVER_HOST, config.REPORT_SERVER_PORT, config.REPORT_SERVER_PATH),
        json=judge_report)



def runserver(port=config.JUDGE_SERVER_PORT):
    app.run(host=config.JUDGE_SERVER_HOST, port=port)


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            server_port = int(sys.argv[1])
            logger.log_info('starting server on custom port', server_port)
            runserver(server_port)
        else:
            logger.log_info('starting server on default port')
            runserver()
    except KeyboardInterrupt:
        exit(0)
