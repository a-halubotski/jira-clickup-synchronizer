from os import environ


class Config():
    """Configuration"""
    jira_webhook_secret = environ.get('JiraWebhookSecret')
    jira_webhook_id = environ.get('JiraWebhookId')
    jira_base_url = environ.get('JiraBaseUrl')
    jira_username = environ.get('JiraUsername')
    jira_api_key = environ.get('JiraApiKey')
    clickup_api_key = environ.get('ClickUpApiKey')
    clickup_account_id = environ.get('ClickUpAccountId')
    

CONFIG = Config()