variable "location" {
  default     = "westeurope"
  description = "Location of the resources."
}

variable "project_tag" {
  default = "jira2clickup"
}

# Web App config
variable "webapp_port" {
  default = 80
  type    = number
}

variable "webapp_log_level" {
  default = "Verbose"
}

variable "Environment" {
  default = {
    "dev" : "Production"
  }
  description = "Yes, production. :)"
}

variable "jira_webhook_secret" {
}

variable "jira_base_url" {
}

variable "jira_user_name" {
}

variable "jira_api_key" {
}

variable "jira_webhook_identifier" {
}

variable "clickup_api_key" {
}

variable "clickup_account_id" {
}
