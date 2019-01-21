
#### judge request data model
```json
{
    "team_id": 103,
    "phase_id": 1,
    "trial_id": 5,
    "dataset_number": 517,
    "submissions": [
        {
            "question_id": 27,
            "question_type": "multi_choice",
            "submitted_answer": "<USER SUMBISSION HERE>"
        },
        {
            "question_id": 29,
            "question_type": "file_upload",
            "submitted_answer": "<FILE URL>"
        }
    ]
}
```


#### judge report data model
```json
{
    "team_id": 103,
    "phase_id": 1,
    "trial_id": 5,
    "dataset_number": 517,
    "submissions": [
        {
            "question_id": 27,
            "score": 0.3
        },
        {
            "question_id": 29,
            "score": 0.5
        }
    ]
}
```
