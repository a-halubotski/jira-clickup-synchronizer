# Configure the Azure provider
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}
variable "subscription_id" {}

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3"
    }
  }

  required_version = ">= 1.3"

  backend "azurerm" {
    key = "jira2clickup.tfstate"
  }
}

provider "azurerm" {
  client_id       = var.client_id
  client_secret   = var.client_secret
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id

  features {
    # this is because Azure creates additional 'invisible' resource in the group that prevents the group deletion
    # resource_group {
    #   prevent_deletion_if_contains_resources = false
    # }
  }
}
