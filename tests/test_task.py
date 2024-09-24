import json
import pytest


from data_private import USERS_TO_CLICKUP
from models.clickup_task import TaskModel
from models.jira_issue import IssueModel

USERS_TO_CLICKUP['Andrew H.'] = 666

@pytest.fixture()
def issue() -> IssueModel:
    with open('docs/jira-webhook-issue.payload.json', 'r') as file:
        return IssueModel(**json.load(file))


def test_task_from_issue(issue: IssueModel):
    t = TaskModel.from_issue(issue)
    # logging.info(t.as_json())
