from json import JSONDecodeError
import logging
import time
from typing import Dict
import requests

from config import CONFIG, Config
from models.clickup_task import TaskModel, TaskUpdateModel
from models.task_comment import TaskCommentModel


class ClickUpService(object):

    def __init__(self, config: Config) -> None:
        # self._config = config
        self._headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": config.clickup_api_key
        }

    def get_task(self, task_id) -> TaskModel:
        task_json = self._call_function(requests.get, f'v2/task/{task_id}')
        return TaskModel.from_api(task_json) if task_json else None

    def create_task(self, task: TaskModel, list_id: str) -> TaskModel:
        logging.info(f'[ClickUpService.create_task] Creating task in list {list_id}')

        created_json = self._call_function(requests.post, f'v2/list/{list_id}/task', payload=task.as_json())
        return TaskModel.from_api(created_json) if created_json else None

    def update_task(self, task: TaskUpdateModel):
        logging.info(f'[ClickUpService.update_task] Updating task {task.id}')
        self._call_function(requests.put, f'v2/task/{task.id}', payload=task.as_json())

    def create_comment(self, comment: TaskCommentModel):
        logging.info(f'[ClickUpService.create_comment] Creating comment {comment.as_json()}')
        self._call_function(requests.post, f'v2/task/{comment.task_id}/comment', payload=comment.as_json())

    def _call_function(self, method, url, args=None, payload=None) -> Dict:
        url = f'https://api.clickup.com/api/{url}'

        if args:
            url = f'{url}{args}'
        logging.info(f'[ClickUpService._call_function] Querying: {method.__name__} url="{url}"')

        if payload:
            logging.info(f'Payload: {payload}')

        startTime = time.time()
        response: requests.Response = method(url, headers=self._headers, json=payload)
        execTime = int((time.time() - startTime)*1000)
        logging.info(f'[ClickUpService._call_function] Executed in {execTime} ms. Status: {response.status_code}')

        if response.status_code == 404:
            logging.warning(f'[ClickUpService._call_function] Not Found.')
            return None

        response_json = None
        try:
            response_json = response.json()
        except JSONDecodeError as ex:
            # not a json, just ignore
            logging.warning(f'[ClickUpService._call_function] Unparsable response: {ex}')

        if response.status_code // 100 != 2:
            logging.error(
                f'[ClickUpService._call_function] Status:{response.status_code}, Headers: {response.headers}, Error Response: {response_json}')
            return None

        return response_json


CLICKUP_SERVICE = ClickUpService(CONFIG)
