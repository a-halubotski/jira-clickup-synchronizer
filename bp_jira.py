"""Blueprint for JIRA issue management
"""
import logging
import json

import azure.functions as func
from azure.functions.decorators.core import AuthLevel
from exceptions.NotAuthorizedException import NotAuthorizedException
from models.jira_comment import IssueCommentModel
from models.jira_issue import IssueModel
from modules.orchestrator import ORCHESTATOR
from utils import authenticate_request

APPLICATION_JSON_MIMETYPE = 'application/json'

bp = func.Blueprint()


@bp.function_name(name="OnJiraIssueWebhook")
@bp.route(route="jira/issue/webhook", methods=['POST', 'PUT'], auth_level=AuthLevel.ANONYMOUS)
def on_jira_issue_webhook(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('[bp_jira.on_jira_issue_webhook]: Request received...')
    req_body = req.get_json()

    # logging.info('HEADERS')
    # for key in req.headers.keys():
    #     logging.info(f'{key} -> {req.headers[key]}')

    try:
        authenticate_request(req)
        logging.info(json.dumps(obj=req_body))
        issue = IssueModel.from_webhook(req_body)
        ORCHESTATOR.sync_issue_to_clickup(issue)

        return func.HttpResponse(status_code=200, mimetype=APPLICATION_JSON_MIMETYPE)
    except NotAuthorizedException:
        logging.warning('Not Authorized')
        return func.HttpResponse(status_code=403)

    except Exception as ex:
        logging.error(ex, stack_info=True)

        error_json = {
            'error': str(ex)
        }

        return func.HttpResponse(
            body=json.dumps(error_json),
            status_code=500
        )

@bp.function_name(name="OnJiraCommentWebhook")
@bp.route(route="jira/comment/webhook", methods=['POST', 'PUT'], auth_level=AuthLevel.ANONYMOUS)
def on_jira_comment_webhook(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('[bp_jira.on_jira_comment_webhook]: Request received...')
    req_body = req.get_json()

    # logging.debug('HEADERS')
    # for key in req.headers.keys():
    #     logging.debug(f'{key} -> {req.headers[key]}')

    try:
        authenticate_request(req)
        logging.info(json.dumps(obj=req_body))
        comment = IssueCommentModel.from_webhook(req_body)
        ORCHESTATOR.sync_comment_to_clickup(comment)

        return func.HttpResponse(status_code=200, mimetype=APPLICATION_JSON_MIMETYPE)
    except NotAuthorizedException:
        return func.HttpResponse(status_code=403)

    except Exception as ex:
        logging.error(ex, stack_info=True)

        error_json = {
            'error': str(ex)
        }

        return func.HttpResponse(
            body=json.dumps(error_json),
            status_code=500
        )
