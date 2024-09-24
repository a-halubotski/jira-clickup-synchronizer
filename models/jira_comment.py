
import json
from utils import attrN


class IssueCommentModel(object):

    def __init__(self, **kwargs) -> None:
        comment = attrN(kwargs, 'comment')
        self.id = attrN(comment, 'id')
        self.body = attrN(comment, 'body')

        issue = attrN(kwargs, 'issue')
        self.issue_key = attrN(issue, 'key')
        self.author = {
            'id': attrN(comment, 'author.accountId'),
            'name': attrN(comment, 'author.displayName')
        }

    @classmethod
    def from_webhook(cls, webhook_json):
        return cls(**webhook_json)

    def as_json(self) -> None:
        return json.dumps(self.__dict__)
