
import json
from models.clickup_comment import ClickupCommentModel
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

    @classmethod
    def from_clickup_model(cls, key: str, clickup_model: ClickupCommentModel):
        body = {
            'issue': {
                'key': key
            },
            'comment': {
                'body': clickup_model.comment,
                'author': {
                    'displayName': clickup_model.creator_name
                }
            }
        }
        return cls(**body)

    def as_update_model(self):
        return {
            'body': {
                'content': [
                    {
                        'content': [
                            {
                                'text': f"Comment by {self.author['name']}",
                                'type': 'text'
                            }
                        ],
                        'type': 'paragraph'
                    },
                    {
                        'content': [
                            {
                                'text': self.body,
                                'type': 'text'
                            }
                        ],
                        'type': 'paragraph'
                    }
                ],
                "type": "doc",
                "version": 1
            }
        }

    def as_json(self) -> None:
        return json.dumps(self.__dict__)
