
## Locals
locals {
  common_tags = {
    Environment = terraform.workspace
    Project     = var.project_tag
  }

  func_name            = "${terraform.workspace}-${var.project_tag}-${var.location}"
  storage_account_name = replace("${terraform.workspace}-st-${var.project_tag}-pl", "-", "")
}

## Resources
resource "azurerm_resource_group" "rg" {
  name     = "${terraform.workspace}-rg-${var.project_tag}-${var.location}"
  location = var.location
  tags     = merge(local.common_tags, { Name = "${terraform.workspace}-rg-${var.project_tag}-${var.location}" })
}

# App Service
resource "azurerm_service_plan" "asp" {
  name                = "${terraform.workspace}-asp-${var.project_tag}-${var.location}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1"

  tags = merge(local.common_tags, { Name = "${terraform.workspace}-asp-${var.project_tag}-${var.location}" })
}

# Storage account
resource "azurerm_storage_account" "sa" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  access_tier              = "Hot"

  https_traffic_only_enabled = true

  blob_properties {
    versioning_enabled = false

    container_delete_retention_policy {
      days = 1
    }
  }

  tags = merge(local.common_tags, { Name = local.storage_account_name })
}

# Log analytics workspace
resource "azurerm_log_analytics_workspace" "loganalytics" {
  name                = "${terraform.workspace}-law-${var.project_tag}-${var.location}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = merge(local.common_tags, { Name = "${terraform.workspace}-law-${var.project_tag}-${var.location}" })
}

# Application Insights
resource "azurerm_application_insights" "appi" {
  name                = "${terraform.workspace}-appi-${var.project_tag}-${var.location}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  application_type  = "web"
  retention_in_days = (terraform.workspace == "dev" ? 30 : 90)
  workspace_id      = azurerm_log_analytics_workspace.loganalytics.id


  tags = merge(local.common_tags, { Name = "${terraform.workspace}-appi-${var.project_tag}-${var.location}" })
}

resource "azurerm_linux_function_app" "func" {
  # workaround to keep the previous function domain name
  name                = local.func_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key
  service_plan_id            = azurerm_service_plan.asp.id

  functions_extension_version = "~4"
  https_only                  = true

  site_config {
    worker_count  = 1
    always_on     = false
    http2_enabled = true

    application_insights_key               = azurerm_application_insights.appi.instrumentation_key
    application_insights_connection_string = azurerm_application_insights.appi.connection_string

    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    AzureWebJobsFeatureFlags = "EnableWorkerIndexing"

    JiraWebhookSecret = var.jira_webhook_secret
    JiraBaseUrl       = var.jira_base_url
    JiraUsername      = var.jira_user_name
    JiraApiKey        = var.jira_api_key


    ClickUpApiKey    = var.clickup_api_key
    ClickUpAccountId = var.clickup_account_id

    WEBSITE_ENABLE_SYNC_UPDATE_SITE = false
    WEBSITE_WEBDEPLOY_USE_SCM       = true
  }

  tags = merge(local.common_tags, { Name = local.func_name })
}
