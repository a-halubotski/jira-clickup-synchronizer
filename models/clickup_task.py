

from typing import List
from datetime import datetime

from data import STATUS_TO_CLICKUP
from data_private import USERS_TO_CLICKUP
from models.jira_issue import IssueModel
from utils import attrN


class TaskModel(object):

    def __init__(self, **kwargs) -> None:
        self.id = attrN(kwargs, 'id')
        self.name = attrN(kwargs, 'name')
        self.description = attrN(kwargs, 'description')
        self.markdown_description = attrN(kwargs, 'markdown_description') or self.description
        self.status = attrN(kwargs, 'status') or attrN(kwargs, 'status.status')
        self.priority = attrN(kwargs, 'priority') or attrN(kwargs, 'priority.id')
        self.assignees = kwargs['assignees'] if 'assignees' in kwargs else []
        self.parent = attrN(kwargs, 'parent')
        self.due_date = attrN(kwargs, 'due_date')
        self.due_date_time = False
        self.start_date = attrN(kwargs, 'start_date')
        self.start_date_time = False

    @classmethod
    def from_issue(cls, issue: IssueModel):
        mapped_status = STATUS_TO_CLICKUP[issue.status['name']] if (
            issue.status['name'] in STATUS_TO_CLICKUP) else STATUS_TO_CLICKUP['Backlog']
        mapped_user = USERS_TO_CLICKUP[issue.assignee['name']] if (issue.assignee['name'] in USERS_TO_CLICKUP) else None
        parent_id = issue.parent.clickup_id if issue.parent else None
        # convert '2024-09-14' -> 1726264800000
        start_date = int(datetime.strptime(issue.start_date, '%Y-%m-%d').timestamp())*1000 if issue.start_date else None
        due_date = int(datetime.strptime(issue.due_date, '%Y-%m-%d').timestamp())*1000 if issue.due_date else None

        body = {
            'id': issue.clickup_id,
            'name': issue.summary,
            'description': issue.description,
            'status': mapped_status,
            'priority': 3,
            'assignee': mapped_user,
            'parent': parent_id,
            'due_date': due_date,
            'start_date': start_date
        }

        return cls(**body)
    
    @classmethod
    def from_api(cls, api_response):
        return cls(**api_response)

    def as_json(self):
        return self.__dict__

"""ClickUp Task model sutable for updating the task
"""
class TaskUpdateModel(TaskModel):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @classmethod
    def from_issue(cls, issue: IssueModel, add_assignees: List[int], remove_assingees: List[int]):
        mapped_status = STATUS_TO_CLICKUP[issue.status['name']] if (
            issue.status['name'] in STATUS_TO_CLICKUP) else STATUS_TO_CLICKUP['Backlog']
        parent_id = issue.parent.clickup_id if issue.parent else None
        # convert '2024-09-14' -> 1726264800000
        start_date = int(datetime.strptime(issue.start_date, '%Y-%m-%d').timestamp())*1000 if issue.start_date else None
        due_date = int(datetime.strptime(issue.due_date, '%Y-%m-%d').timestamp())*1000 if issue.due_date else None

        body = {
            'id': issue.clickup_id,
            'name': issue.summary,
            'description': issue.description,
            'status': mapped_status,
            'priority': 3,            
            'parent': parent_id,
            'due_date': due_date,
            'start_date': start_date            
        }

        task = cls(**body)
        task.assignees = {
            'add': add_assignees,
            'rem': remove_assingees
        }

        return task
    