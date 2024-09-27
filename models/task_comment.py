
from typing import Dict
from data import DEFAULT_ASSIGNEE
from data_private import USERS_TO_CLICKUP
from models.jira_comment import IssueCommentModel
from utils import attrN


class TaskCommentModel(object):
    def __init__(self, **kwargs) -> None:
        self.task_id = attrN(kwargs, 'task_id')
        self.comment_text = attrN(kwargs, 'comment_text')
        self.assignee = attrN(kwargs, 'assignee')

    @classmethod
    def from_issue_model(cls, clickup_id: str, comment: IssueCommentModel):
        author_id = DEFAULT_ASSIGNEE # USERS_TO_CLICKUP[comment.author['name']] if (comment.author['name'] in USERS_TO_CLICKUP) else None
        body = {
            'task_id': clickup_id,
            'jira_comment_id': comment.id,
            'comment_text': comment.body,
            # 'assignee': author_id
        }
        return cls(**body)

    def as_json(self) -> Dict:
        return {
            'notify_all': False,
            'comment_text': self.comment_text,
            # 'assignee': self.assignee
        }
