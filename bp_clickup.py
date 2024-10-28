"""Blueprint for JIRA issue management
"""
import logging
import json

import azure.functions as func
from azure.functions.decorators.core import AuthLevel
from exceptions.NotAuthorizedException import NotAuthorizedException
from models.clickup_comment import ClickupCommentModel
from modules.orchestrator import ORCHESTATOR

APPLICATION_JSON_MIMETYPE = 'application/json'

bp = func.Blueprint()


@bp.function_name(name="OnClickUpCommentWebhook")
@bp.route(route="clickup/comment/webhook", methods=['POST', 'PUT'], auth_level=AuthLevel.ANONYMOUS)
def on_clickup_comment_webhook(req: func.HttpRequest) -> func.HttpResponse:

    logging.info(f'[bp_clickup.on_clickup_comment_webhook]: Request received... {req.url}')
    req_body = req.get_json()

    logging.debug('HEADERS')
    for key in req.headers.keys():
        logging.info(f'{key} -> {req.headers[key]}')

    try:
        # authenticate_request(req)
        logging.info(json.dumps(obj=req_body))
        clickup_comment = ClickupCommentModel.from_webhook(req_body)
        ORCHESTATOR.sync_comment_to_jira(clickup_comment)

        return func.HttpResponse(status_code=200, mimetype=APPLICATION_JSON_MIMETYPE)
    except NotAuthorizedException:
        logging.error(ex)
        return func.HttpResponse(status_code=200)

    except Exception as ex:
        logging.error(ex, stack_info=True)

        error_json = {
            'error': str(ex)
        }

        return func.HttpResponse(
            body=json.dumps(error_json),
            status_code=200
        )
