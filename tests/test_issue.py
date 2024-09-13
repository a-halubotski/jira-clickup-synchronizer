import json

import pytest


from data import USERS_TO_CLICKUP
from models.jira_issue import IssueModel

USERS_TO_CLICKUP['Andrew H.'] = 666

@pytest.fixture()
def issue() -> IssueModel:
    with open('docs/jira-webhook-issue.payload.json', 'r') as file:
        return IssueModel(**json.load(file))

@pytest.fixture()
def issue_with_parent() -> IssueModel:
    with open('docs/jira-webhook-issue-with-parent.payload.json', 'r') as file:
        return IssueModel(**json.load(file))

def test_ticket_model_parsing(issue: IssueModel):
    assert 'jira:issue_created' == issue.event
    assert '52814' == issue.id
    assert 'ALUM-71' == issue.key
    assert 'ALUM' == issue.project_key
    #
    assert '7' == issue.type['id']
    assert 'Story' == issue.type['name']
    #
    assert '10011' == issue.status['id']
    assert 'Backlog' == issue.status['name']
    #
    assert '712020:4a12a0a3-a1f6-4d67-a8b0-e3fd205e111a' == issue.assignee['id']
    assert 'Andrew H.' == issue.assignee['name']

def test_ticket_model_parsing_with_parent(issue_with_parent: IssueModel):
    assert 'jira:issue_created' == issue_with_parent.event
    assert 'ALUM-74' == issue_with_parent.parent_key
