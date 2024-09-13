import azure.functions as func
from typing import Dict

from config import CONFIG
from exceptions.NotAuthorizedException import NotAuthorizedException

"""Safely returns attribute value"""


def attr_safe(obj: Dict, attr: str, default=None):
    return obj[attr] if attr and obj and (attr in obj) and obj[attr] else default


"""Safely returns first element of array"""


def attr0(obj, attr, default=None):
    found = attr_safe(obj, attr, default)
    if found and isinstance(found, list) and len(found):
        return found[0]
    else:
        return found


"""Safely returns any nested element"""


def attrN(obj, attr: str, default=None):
    attrs = attr.split('.')
    found = attr0(obj, attrs[0], default)

    if len(attrs) == 1 or not found:
        # last element
        return found

    attr = attr[attr.index('.')+1:]
    return attrN(found, attr, default)


def authenticate_request(req: func.HttpRequest):
    if validate_header(req.headers, 'x-atlassian-webhook-identifier', CONFIG.jira_webhook_id) \
            and validate_header(req.headers, 'user-agent', 'Atlassian Webhook HTTP Client'):
        return

    raise NotAuthorizedException('Not authorized')

def validate_header(headers, name, value) -> bool:
    return name in headers.keys() and headers[name] == value
