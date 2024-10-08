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


@bp.function_name(name="OnClickUpCommentWebhook")
@bp.route(route="clickup/comment/webhook/{task_id}", methods=['POST', 'PUT'], auth_level=AuthLevel.ANONYMOUS)
def on_clickup_comment_webhook(req: func.HttpRequest) -> func.HttpResponse:

    logging.info(f'[bp_clickup.on_clickup_comment_webhook]: Request received... {req.url}')
    req_body = req.get_json()
    task_id = req.route_params.get('task_id')


    logging.debug('HEADERS')
    for key in req.headers.keys():
        logging.info(f'{key} -> {req.headers[key]}')

    try:
        # authenticate_request(req)
        logging.info(json.dumps(obj=req_body))
        # comment = IssueCommentModel.from_webhook(req_body)
        # ORCHESTATOR.sync_comment_to_clickup(comment)

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
