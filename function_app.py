"""JIRA to ClickUp integration function
"""

import azure.functions as func

from bp_jira import bp as issue_blueprint

app = func.FunctionApp()

app.register_blueprint(issue_blueprint)
