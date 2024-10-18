
import json
from utils import attrN


class ClickupCommentModel(object):

    def __init__(self, **kwargs) -> None:
        self.id = attrN(kwargs, 'id')
        self.task_id = attrN(kwargs, 'parent')
        self.comment = attrN(kwargs, 'text_content')
        self.creator_name = attrN(kwargs, 'user.username')

    @classmethod
    def from_webhook(cls, webhook_json):
        comment_json = attrN(webhook_json, 'history_items.comment')
        return cls(**comment_json)

    def as_json(self) -> None:
        return json.dumps(self.__dict__)
