"""JIRA to ClickUp integration function and back.
"""

import azure.functions as func

from bp_jira import bp as jira_blueprint
from bp_clickup import bp as clickup_blueprint

app = func.FunctionApp()

app.register_blueprint(jira_blueprint)
app.register_blueprint(clickup_blueprint)
