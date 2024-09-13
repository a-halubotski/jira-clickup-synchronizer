import json
import logging
import time
import requests

from json import JSONDecodeError
from typing import Dict
from requests.auth import HTTPBasicAuth

from config import CONFIG, Config
from models.jira_issue import IssueModel


class JiraService(object):

    def __init__(self, config: Config) -> None:
        self._config = config
        self._headers: Dict[str, str] = {
            "Content-Type": "application/json"
        }
        self._auth = HTTPBasicAuth(config.jira_username, config.jira_api_key)

    def get_issue(self, key: str) -> IssueModel:
        logging.info(f'[JiraService.get_issue] Getting issue: {key}')
        issue_json = self._call_function(requests.get, f'issue/{key}')
        return IssueModel.from_api(issue_json)

    def update_issue_clickup_id(self, issue_key: str, clickup_id: str):
        logging.info(f"[JiraService.update_issue_clickup_id] Assigning ClickUp ID '{clickup_id}' to JIRA issue '{issue_key}'")
        self._call_function(requests.put, f'issue/{issue_key}', args='notifyUsers=false', payload={'fields': {'customfield_11257': clickup_id}})

    def _call_function(self, method, url, args=None, payload=None) -> Dict:
        url = f'{self._config.jira_base_url}/rest/api/3/{url}'

        if args:
            url = f'{url}?{args}'
        logging.info(f'[JiraService._call_function] Querying: url="{url}"')

        if payload:
            logging.info(f'Payload: {payload}')
        startTime = time.time()
        response: requests.Response = method(url, headers=self._headers, json=payload, auth=self._auth)
        execTime = int((time.time() - startTime)*1000)
        logging.info(f'[JiraService._call_function] Executed in {execTime} ms. Status: {response.status_code}')

        if response.status_code == 404:
            logging.warning(f'[JiraService._call_function] Not Found.')
            return None
        
        if response.status_code == 204:
            return None

        response_json = {}
        try:
            response_json = response.json()
        except JSONDecodeError as ex:
            # not a json, just ignore
            logging.warning(f'[JiraService._call_function] Unparsable response: {ex}')

        if response.status_code // 100 != 2:
            logging.error(
                f'[JiraService._call_function] Status:{response.status_code}, Headers: {response.headers}, Error Response: {response_json}')
            return None

        return response_json


JIRA_SERVICE = JiraService(CONFIG)
