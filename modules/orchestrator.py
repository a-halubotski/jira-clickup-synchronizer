
import logging
import json

from data_private import PROJECT_MAPPING, USERS_TO_CLICKUP
from models.clickup_comment import ClickupCommentModel
from models.clickup_task import TaskModel, TaskUpdateModel
from models.jira_comment import IssueCommentModel
from models.jira_issue import IssueModel
from models.task_comment import TaskCommentModel
from modules.clickup_service import CLICKUP_SERVICE, ClickUpService
from modules.jira_service import JIRA_SERVICE, JiraService

CLICKUP_PIVOTICS_DEV_USER_ID = 88206996
JIRA_USER_FOR_CLICKUP_COMMENTS = "712020:e673ab54-0a31-44ca-887d-99ce7b45d856"


class Orchestrator(object):

    def __init__(self, jira_service: JiraService, clickup_service: ClickUpService) -> None:
        self._jira = jira_service
        self._clickup = clickup_service

    def sync_issue_to_clickup(self, issue: IssueModel):
        logging.info(f'[Orchestrator.sync_ticket_to_clickup] Commence JIRA issue: {issue.key}')

        if not issue.project_key in PROJECT_MAPPING:
            raise Exception(f'[Orchestrator.sync_ticket_to_clickup] Unknown JIRA project: {issue.project_key}')

        if issue.parent_key:
            # initialize with parent (sorry, immutability)
            logging.info(f'[Orchestrator.sync_ticket_to_clickup] Getting JIRA parent issue: {issue.parent_key}')
            issue.parent = self._jira.get_issue(issue.parent_key)

        task: TaskModel = None
        is_new: bool = True

        if (not issue.clickup_id):
            # issue not synced before
            task = self._create_task(issue)
        else:
            logging.info(f'[Orchestrator.sync_ticket_to_clickup] Updating existing ClickUp task: {issue.clickup_id}')
            task = self._clickup.get_task(issue.clickup_id)

            if not task:
                # hey, where is my task?!
                logging.info(f'[Orchestrator.sync_ticket_to_clickup] Task not found, creating it back.')
                task = self._create_task(issue)
            else:
                self._update_task(issue, task)
                is_new = False

        # Assign task to Sprint
        if issue.sprint != None and is_new:
            self._add_task_to_sprint(task, issue.sprint)
        else:
            self._sync_task_sprints(task, issue)

    def sync_comment_to_clickup(self, comment: IssueCommentModel):
        logging.info(f'[Orchestrator.sync_comment_to_clickup] Comment: {comment.as_json()}')
        # Do not sync comments added from ClickUp
        if comment.is_private():
            logging.warning("Private JIRA comment")
            return
        if comment.author['id'] == JIRA_USER_FOR_CLICKUP_COMMENTS:
            logging.warning("Self JIRA comment")
            return

        issue: IssueModel = self._jira.get_issue(comment.issue_key)
        if not issue or not issue.clickup_id:
            logging.info(f'[Orchestrator.sync_comment_to_clickup] Issue not synchronized: {comment.issue_key}')
            return

        task_comment = TaskCommentModel.from_issue_model(issue.clickup_id, comment)

        self._clickup.create_comment(task_comment)

    def sync_comment_to_jira(self, clickup_comment: ClickupCommentModel):
        logging.info(f'[Orchestrator.sync_comment_to_jira] Task: {clickup_comment.as_json()}')
        # Check if it's not automated comment syncronized from JIRA.
        if clickup_comment.creator_id == CLICKUP_PIVOTICS_DEV_USER_ID:
            logging.info(f'[Orchestrator.sync_comment_to_jira] Self ClickUp comment')
            return

        # Find JIRA task
        jira_issue = self._jira.get_issue_by_clickup_id(clickup_comment.task_id)
        if jira_issue and jira_issue.key != None:
            jira_comment = IssueCommentModel.from_clickup_model(key=jira_issue.key, clickup_model=clickup_comment)
            self._jira.create_issue_comment(jira_comment)

    def _create_task(self, issue: IssueModel):
        list_id = PROJECT_MAPPING[issue.project_key]
        task = TaskModel.from_issue(issue)
        task = self._clickup.create_task(task, list_id)
        self._jira.update_issue_clickup_id(issue.key, task.id)

        return task

    def _update_task(self, issue: IssueModel, task: TaskModel):
        current_assignees = list(map(lambda it: it['id'], task.assignees))
        new_assignee = USERS_TO_CLICKUP[issue.assignee['name']] if issue.assignee['name'] in USERS_TO_CLICKUP else None

        if new_assignee in current_assignees:
            current_assignees.remove(new_assignee)

        task_for_update = TaskUpdateModel.from_issue(issue, [new_assignee], current_assignees)
        return self._clickup.update_task(task_for_update)

    def _add_task_to_sprint(self, task: TaskModel, sprint_name: str):
        sprint_list_id = self._clickup.find_sprint_list_id_by_name(sprint_name)
        if sprint_list_id:
            self._clickup.add_task_to_list(task.id, sprint_list_id)

    def _sync_task_sprints(self, task: TaskModel, issue: IssueModel):
        if issue.sprint != None:
            self._add_task_to_sprint(task, issue.sprint.name)


ORCHESTATOR = Orchestrator(JIRA_SERVICE, CLICKUP_SERVICE)
