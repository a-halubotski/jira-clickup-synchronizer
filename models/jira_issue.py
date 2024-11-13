"""JIRA Issue model
"""
import json
from typing import Dict

from utils import attr_safe, attrN


class JiraSprintModel(object):

    def __init__(self, **kwargs):
        self.id = attrN(kwargs, 'id')
        self.name = attrN(kwargs, 'name')

    @classmethod
    def from_webhook(cls, webhook_json: Dict):
        """'fields' object expected"""
        sprints = attr_safe(webhook_json, 'customfield_10007')

        if sprints == None:
            return

        for sprint in sprints:
            if sprint['state'] == 'active':
                return cls(**sprint)

        # if no active sprints: pick the last one
        return cls(**sprints[-1]) if sprints is not None and len(sprints) > 0 else None


class IssueModel(object):

    def __init__(self, **kwargs) -> None:
        self.event = attrN(kwargs, 'webhookEvent') or attrN(kwargs, 'webhookEvent')

        issue = attrN(kwargs, 'issue')
        self.id = attrN(issue, 'id')
        self.key = attrN(issue, 'key')

        fields = attrN(issue, 'fields')
        self.project_key = attrN(fields, 'project.key')
        self.summary = attrN(fields, 'summary')
        self.description = attrN(fields, 'description')
        self.assignee = {
            'id': attrN(fields, 'assignee.accountId'),
            'name': attrN(fields, 'assignee.displayName')
        }
        self.type = {
            'id': attrN(fields, 'issuetype.id'),
            'name': attrN(fields, 'issuetype.name')
        }
        self.status = {
            'id': attrN(fields, 'status.id'),
            'name': attrN(fields, 'status.name')
        }
        self.start_date = attrN(fields, 'customfield_11222')
        self.due_date = attrN(fields, 'duedate')

        self.clickup_id = attrN(fields, 'customfield_11257')
        self.parent_key = attrN(fields, 'parent.key')

        self.sprint = JiraSprintModel.from_webhook(fields)

        self.parent = None

    @classmethod
    def from_api(cls, api_json: Dict):
        # we don't need much from the api all because so far it's used to get parent and it's clickup id.
        fields = attrN(api_json, 'fields')
        body = {
            'issue': {
                'id': attrN(api_json, 'id'),
                'key': attrN(api_json, 'key'),
                'fields': {
                    'customfield_11257': attrN(fields, 'customfield_11257'),
                }
            }
        }
        return cls(**body)

    @classmethod
    def from_webhook(cls, webhook_json: Dict):
        return cls(**webhook_json)

    def as_json(self) -> None:
        return json.dumps(self.__dict__)
